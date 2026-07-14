# ==========================================================
# Imports + Initialization + Persistent Parent Store
# ==========================================================

import json
import re
import uuid

import os
import gc

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import chromadb

from sentence_transformers import SentenceTransformer

from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    EMBEDDING_MODEL,
    PARENT_CHUNK_SIZE,
    PARENT_CHUNK_OVERLAP,
    CHILD_CHUNK_SIZE,
    CHILD_CHUNK_OVERLAP,
    TOP_K_CHILDREN,
    MAX_PARENT_CONTEXT,
    PARENT_STORE_PATH,
    CHROMA_DB_PATH,
    COLLECTION_NAME,
    EMBEDDING_BATCH_SIZE
)


class RAGPipeline:

    def __init__(self):

        # ==================================================
        # Embedding Model
        # ==================================================

        self.embedding_model = SentenceTransformer(

            EMBEDDING_MODEL,

            device="cpu"

        )


        # ==================================================
        # Parent Splitter
        # ==================================================

        self.parent_splitter = RecursiveCharacterTextSplitter(

            chunk_size=PARENT_CHUNK_SIZE,

            chunk_overlap=PARENT_CHUNK_OVERLAP

        )

        # ==================================================
        # Child Splitter
        # ==================================================

        self.child_splitter = RecursiveCharacterTextSplitter(

            chunk_size=CHILD_CHUNK_SIZE,

            chunk_overlap=CHILD_CHUNK_OVERLAP

        )

        # ==================================================
        # ChromaDB
        # ==================================================

        print("=" * 60)
        print(f"CHROMA_DB_PATH: {CHROMA_DB_PATH}")
        print(f"RAILWAY_PUBLIC_DOMAIN: {os.getenv('RAILWAY_PUBLIC_DOMAIN')}")
        print(f"PORT: {os.getenv('PORT')}")
        print("=" * 60)

        self.client = chromadb.PersistentClient(

            path=CHROMA_DB_PATH

        )

        # ==================================================
        # Always start with an empty knowledge base
        # ==================================================
        
        try:

            self.client.delete_collection(COLLECTION_NAME)

        except Exception:

            pass

        self.collection = self.client.create_collection(

            name=COLLECTION_NAME

        )

       
        # ==================================================
        # Parent Store File
        # ==================================================

        self.parent_store_file = PARENT_STORE_PATH

        with open(

            self.parent_store_file,

            "w",

            encoding="utf-8"

        ) as f:

            json.dump(

                {},

                f

            )

        self.parent_store = self.load_parent_store()

        # ==================================================
        # BM25 Index
        # ==================================================

        self.bm25 = None
        self.bm25_documents = []


# ==========================================================
# Parent Store Utility Functions
# ==========================================================

    # ======================================================
    # Load Parent Store
    # ======================================================

    def load_parent_store(self):

        if not os.path.exists(self.parent_store_file):

            return {}

        try:

            with open(

                self.parent_store_file,

                "r",

                encoding="utf-8"

            ) as f:

                return json.load(f)

        except Exception:

            return {}

    # ======================================================
    # Save Parent Store
    # ======================================================

    def save_parent_store(self):

        with open(

            self.parent_store_file,

            "w",

            encoding="utf-8"

        ) as f:

            json.dump(

                self.parent_store,

                f,

                indent=4,

                ensure_ascii=False

            )


# ==========================================================
# Create Parent Chunks
# ==========================================================

    # ======================================================
    # Create Parent Chunks
    # ======================================================

    def create_parent_chunks(self, documents):

        parent_chunks = []

        for document in documents:

            cleaned_text = self.clean_text(

                document["text"]

            )

            split_parents = self.parent_splitter.split_text(

                cleaned_text

            )

            total_parents = len(split_parents)

            for parent_index, parent_text in enumerate(split_parents):

                parent_id = (

                    f"{document['file_name']}_parent_{parent_index+1}"

                )

                parent_data = {

                    "parent_id": parent_id,

                    "text": parent_text,

                    "source": document["file_name"],

                    "parent_number": parent_index + 1,

                    "total_parents": total_parents

                }

                parent_chunks.append(parent_data)

                # ==========================================
                # Save Parent Chunk
                # ==========================================

                self.parent_store[parent_id] = parent_data

        # ==============================================
        # Persist Parent Store
        # ==============================================

        self.save_parent_store()

        return parent_chunks


# ==========================================================
# Create Child Chunks
# ==========================================================

    # ======================================================
    # Create Child Chunks
    # ======================================================

    def create_child_chunks(self, parent_chunks):

        child_chunks = []

        for parent in parent_chunks:

            split_children = self.child_splitter.split_text(

                parent["text"]

            )

            total_children = len(split_children)

            for child_index, child_text in enumerate(split_children):

                child_chunks.append({

                    "id": f"{parent['parent_id']}_child_{child_index+1}",

                    "text": child_text,

                    "parent_id": parent["parent_id"],

                    "source": parent["source"],

                    "parent_number": parent["parent_number"],

                    "total_parents": parent["total_parents"],

                    "child_number": child_index + 1,

                    "total_children": total_children

                })

        print(

            f"\nCreated {len(child_chunks)} Child Chunks "

            f"from {len(parent_chunks)} Parent Chunks."

        )

        return child_chunks
    

# ==========================================================
# Generate Embeddings + Store Child Embeddings
# ==========================================================

    # ======================================================
    # Generate Embeddings
    # ======================================================

    def generate_embeddings(self, child_chunks):

        texts = [

            chunk["text"]

            for chunk in child_chunks

        ]

        embeddings = self.embedding_model.encode(

            texts,

            convert_to_numpy=True,

            show_progress_bar=True,

            batch_size=4

        )

        for chunk, embedding in zip(

            child_chunks,

            embeddings

        ):

            chunk["embedding"] = embedding.tolist()

        return child_chunks


    # ======================================================
    # Store Child Embeddings
    # ======================================================

    def store_embeddings(self, child_chunks):

        existing_ids = set(
            self.collection.get(include=[])["ids"]
        )

        new_chunks = 0

        for chunk in child_chunks:

            if chunk["id"] in existing_ids:
                continue

            try:

                self.collection.add(

                    ids=[
                        chunk["id"]
                    ],

                    embeddings=[
                        chunk["embedding"]
                    ],

                    documents=[
                        chunk["text"]
                    ],

                    metadatas=[{
                        "source": str(chunk["source"]),
                        "parent_id": str(chunk["parent_id"]),
                        "parent_number": int(chunk["parent_number"]),
                        "total_parents": int(chunk["total_parents"]),
                        "child_number": int(chunk["child_number"]),
                        "total_children": int(chunk["total_children"])
                    }]

                )

                new_chunks += 1

            except Exception as e:

                print("\n============================")
                print("CHROMADB INSERT ERROR")
                print(type(e))
                print(e)
                print(chunk)
                print("============================\n")

                raise

        print(f"\nStored {new_chunks} Child Chunks in ChromaDB.")


# ==========================================================
# Child Retrieval -> Parent Retrieval -> Context Building
# ==========================================================

    # ======================================================
    # Search Child Chunks
    # ======================================================

    def search_documents(self, query):

        query_embedding = self.embedding_model.encode(

            [query],

            convert_to_numpy=True

        )[0]

        results = self.collection.query(

            query_embeddings=[

                query_embedding.tolist()

            ],

            n_results=TOP_K_CHILDREN,

            include=["documents", "metadatas", "distances"]

        )

        return results


    # ======================================================
    # Normalize Text (for filename matching)
    # ======================================================

    def _normalize_text(self, text):

        text = text.lower()

        text = re.sub(r"[^a-z0-9]+", " ", text)

        return text.strip()


    # ======================================================
    # Detect an Explicitly Named PDF in the Query
    # ======================================================

    def _detect_mentioned_source(self, query):

        sources = {

            parent["source"]

            for parent in self.parent_store.values()

        }

        if not sources:

            return None

        query_norm = self._normalize_text(query)

        best_source = None
        best_score = 0.0

        for source in sources:

            file_stem = os.path.splitext(source)[0]

            tokens = [

                token

                for token in self._normalize_text(file_stem).split()

                if len(token) > 2

            ]

            if not tokens:

                continue

            hits = sum(

                1

                for token in tokens

                if token in query_norm

            )

            score = hits / len(tokens)

            if score > best_score:

                best_score = score

                best_source = source

        if best_score >= 0.6:

            return best_source

        return None


    # ======================================================
    # Retrieve Parent Chunks (Small PDF Heuristic)
    # ======================================================

    def retrieve_parent_chunks(self, results, mentioned_source=None):

        # Reload parent store only when needed
        self.parent_store = self.load_parent_store()

        retrieved_parents = []
        visited = set()

        metadata_list = results["metadatas"][0]
        distance_list = results["distances"][0]

        for metadata, distance in zip(metadata_list, distance_list):

            parent_id = metadata["parent_id"]

            if parent_id in visited:
                continue

            visited.add(parent_id)

            parent = self.parent_store.get(parent_id)

            if parent is None:
                continue

            retrieved_parents.append({

                "parent_id": parent_id,

                "source": parent["source"],

                "parent_number": parent["parent_number"],

                "total_parents": parent["total_parents"],

                "score": round(distance, 4),

                "text": parent["text"]

            })

        # ==================================================
        # Small PDF Heuristic
        # ==================================================

        expanded = []

        for parent in retrieved_parents:

            expanded.append(parent)

            if parent["total_parents"] <= 5:

                for pid, pdata in self.parent_store.items():

                    if (
                        pdata["source"] == parent["source"]
                        and pdata["parent_id"] != parent["parent_id"]
                    ):

                        expanded.append({

                            "parent_id": pdata["parent_id"],

                            "source": pdata["source"],

                            "parent_number": pdata["parent_number"],

                            "total_parents": pdata["total_parents"],

                            "score": parent["score"],

                            "text": pdata["text"]

                        })

        # Remove duplicates

        unique = {}

        for item in expanded:
            unique[item["parent_id"]] = item

        # ==================================================
        # Guarantee representation for very small documents
        # ==================================================
        
        small_doc_sources = {

            pdata["source"]

            for pdata in self.parent_store.values()

            if pdata["total_parents"] <= 5

        }

        represented_sources = {

            item["source"] for item in unique.values()

        }

        for source in small_doc_sources - represented_sources:

            for pid, pdata in self.parent_store.items():

                if pdata["source"] == source:

                    unique[pid] = {

                        "parent_id": pid,

                        "source": pdata["source"],

                        "parent_number": pdata["parent_number"],

                        "total_parents": pdata["total_parents"],

                        "score": 0.5,

                        "text": pdata["text"]

                    }

        # ==================================================
        # Force-include an explicitly named PDF
        # ==================================================
        
        forced_ids = set()

        if mentioned_source:

            for pid, pdata in self.parent_store.items():

                if pdata["source"] == mentioned_source:

                    unique[pid] = {

                        "parent_id": pid,

                        "source": pdata["source"],

                        "parent_number": pdata["parent_number"],

                        "total_parents": pdata["total_parents"],

                        "score": -1,  # force to the front

                        "text": pdata["text"]

                    }

                    forced_ids.add(pid)

        all_parents = list(unique.values())

        forced_parents = [

            p for p in all_parents if p["parent_id"] in forced_ids

        ]

        remaining_parents = [

            p for p in all_parents if p["parent_id"] not in forced_ids

        ]

        remaining_parents.sort(key=lambda x: x["score"])

        remaining_budget = MAX_PARENT_CONTEXT - len(forced_parents)

        if remaining_budget <= 0:

            return sorted(

                forced_parents,

                key=lambda x: x["parent_number"]

            )[:MAX_PARENT_CONTEXT]

        if forced_parents:

            return forced_parents + remaining_parents[:remaining_budget]

        # ==================================================
        # No explicit mention -> round-robin across sources
        # ==================================================
        
        by_source = {}

        for parent in remaining_parents:

            by_source.setdefault(parent["source"], []).append(parent)

        for source_parents in by_source.values():

            source_parents.sort(key=lambda x: x["score"])

        final_parents = []

        source_order = list(by_source.keys())

        round_index = 0

       

        while len(final_parents) < MAX_PARENT_CONTEXT and any(
            round_index < len(by_source[source]) for source in source_order
        ):

            for source in source_order:

                if len(final_parents) >= MAX_PARENT_CONTEXT:

                    break

                bucket = by_source[source]

                if round_index < len(bucket):

                    final_parents.append(bucket[round_index])

            round_index += 1

        return final_parents


    # ======================================================
    # Build Final Context
    # ======================================================

    def build_context(self, parent_chunks):

        context = ""

        for parent in parent_chunks:

            context += (

                f"\n\n"

                f"==============================\n"

                f"Source : {parent['source']}\n"

                f"Parent Chunk : {parent['parent_number']}\n"

                f"==============================\n\n"

                f"{parent['text']}\n"

            )

        return context


    # ======================================================
    # Retrieve Context
    # ======================================================

    def retrieve_context(self, query):

        results = self.search_documents(

            query

        )

        mentioned_source = self._detect_mentioned_source(

            query

        )

        if mentioned_source:

            print(f"Detected explicit PDF mention: {mentioned_source}")

        parent_chunks = self.retrieve_parent_chunks(

            results,

            mentioned_source=mentioned_source

        )

        context = self.build_context(

            parent_chunks

        )

        return context, results


# ==========================================================
# Complete Document Ingestion Pipeline
# ==========================================================

    # ======================================================
    # Complete Ingestion Pipeline
    # ======================================================

    def ingest_documents(self, documents):

        print("\n==================================================")
        print("Starting Parent-Child Indexing...")
        print("==================================================")

        # -----------------------------------------------
        # Parent Chunks
        # -----------------------------------------------

        print("\nCreating Parent Chunks...")

        parent_chunks = self.create_parent_chunks(

            documents

        )

        print(

            f"Created {len(parent_chunks)} Parent Chunks."

        )

        # -----------------------------------------------
        # Child Chunks
        # -----------------------------------------------

        print("\nCreating Child Chunks...")

        child_chunks = self.create_child_chunks(

            parent_chunks

        )

        print(

            f"Created {len(child_chunks)} Child Chunks."

        )

        # -----------------------------------------------
        # Generate + Store Embeddings in Small Batches
        # (Reduces Railway RAM usage)
        # -----------------------------------------------

        print("\nGenerating & Storing Embeddings in Batches...")

        BATCH_SIZE = EMBEDDING_BATCH_SIZE

        for start in range(0, len(child_chunks), BATCH_SIZE):

            # Take only 50 child chunks at a time
            batch = child_chunks[start:start + BATCH_SIZE]

            # Generate embeddings only for this batch
            batch = self.generate_embeddings(batch)

            # Store immediately in ChromaDB
            self.store_embeddings(batch)

            # Remove embeddings from RAM after storing
            for chunk in batch:
                chunk.pop("embedding", None)

            # Delete batch and force garbage collection
            del batch

            gc.collect()


        # -----------------------------------------------
        # Save Parent Store
        # -----------------------------------------------

        print("\n==================================================")
        print("Parent-Child Indexing Completed Successfully")
        print("==================================================")

        print(f"Parent Chunks : {len(parent_chunks)}")
        print(f"Child Chunks  : {len(child_chunks)}")

        print("==================================================\n")

        del child_chunks
        del parent_chunks

        gc.collect()

       
    # ======================================================
    # Clean Text
    # ======================================================

    def clean_text(self, text):

        return " ".join(text.split())