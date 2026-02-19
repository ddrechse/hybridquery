import oracledb
import sys
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime

class OracleGraphLoader:
    """
    Directly loads extracted graph entities into Oracle Database.
    Replaces GraphDataBuilder (CSV generation).
    """

    def __init__(self, user, password, dsn):
        self.user = user
        self.password = password
        self.dsn = dsn
        self.conn = None
        self.cursor = None
        
        # In-memory maps to cache IDs for edge creation (Name -> DB_ID)
        self.treatment_map: Dict[str, int] = {}
        self.condition_map: Dict[str, int] = {}
        
        # Statistics
        self.stats = {
            'papers': 0,
            'treatments': 0,
            'conditions': 0,
            'mentions_edges': 0,
            'treats_edges': 0
        }

    def connect(self):
        """Establish database connection"""
        try:
            print(f"🔌 Connecting to Oracle Database ({self.dsn})...")
            self.conn = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=self.dsn
            )
            self.cursor = self.conn.cursor()
            print("   ✓ Connected successfully")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            sys.exit(1)

    def close(self):
        """Commit and close connection"""
        if self.conn:
            self.conn.commit()
            print("💾 Transaction committed")
            self.cursor.close()
            self.conn.close()
            print("🔌 Connection closed")

    def add_paper(self, filename: str, title: str, publication_date: str = None, 
                  embedding: List[float] = None) -> int:
        """Insert paper and return new Node ID"""
        if not self.conn: self.connect()

        if publication_date is None:
            publication_date = datetime.now().strftime('%Y-%m-%d')
            
        sql = """
            INSERT INTO papers_nodes (filename, title, publication_date, content_embedding)
            VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD'), :4)
            RETURNING node_id INTO :5
        """
        
        # Ensure embedding is compatible (array.array or list)
        import array
        embedding_val = array.array('f', embedding) if embedding else None

        out_id = self.cursor.var(int)
        self.cursor.execute(sql, [filename, title[:500], publication_date, embedding_val, out_id])
        
        new_id = out_id.getvalue()[0]
        self.stats['papers'] += 1
        return new_id

    def add_treatment(self, name: str, treatment_type: str = "Pharmaceutical", 
                      embedding: List[float] = None) -> int:
        """Insert treatment if not exists, return Node ID"""
        if name in self.treatment_map:
            return self.treatment_map[name]
            
        # Check DB first (in case running multiple times or parallel)
        # For simplicity in this POC, we trust the map + unique constraints if we had them.
        # But let's do a quick check or merge.
        # Simplest approach for POC: Insert and handle dupes or check first.
        # Given we just cleared tables or are running fresh, check is fine.
        
        self.cursor.execute("SELECT node_id FROM treatments_nodes WHERE entity_name = :1", [name])
        row = self.cursor.fetchone()
        
        if row:
            node_id = row[0]
        else:
            out_id = self.cursor.var(int)
            sql = """
                INSERT INTO treatments_nodes (entity_name, treatment_type, description_embedding)
                VALUES (:1, :2, :3)
                RETURNING node_id INTO :4
            """
            
            import array
            embedding_val = array.array('f', embedding) if embedding else None

            self.cursor.execute(sql, [name, treatment_type, embedding_val, out_id])
            node_id = out_id.getvalue()[0]
            self.stats['treatments'] += 1
            
        self.treatment_map[name] = node_id
        return node_id

    def add_condition(self, name: str, embedding: List[float] = None) -> int:
        """Insert condition if not exists, return Node ID"""
        if name in self.condition_map:
            return self.condition_map[name]
            
        self.cursor.execute("SELECT node_id FROM conditions_nodes WHERE name = :1", [name])
        row = self.cursor.fetchone()
        
        if row:
            node_id = row[0]
        else:
            # Basic ICD logic
            icd = 'E11' if 'Type 2' not in name else 'E11'
            if 'Type 1' in name: icd = 'E10'
            
            out_id = self.cursor.var(int)
            sql = """
                INSERT INTO conditions_nodes (name, icd10_code, description_embedding)
                VALUES (:1, :2, :3)
                RETURNING node_id INTO :4
            """
            
            import array
            embedding_val = array.array('f', embedding) if embedding else None
            
            self.cursor.execute(sql, [name, icd, embedding_val, out_id])
            node_id = out_id.getvalue()[0]
            self.stats['conditions'] += 1
            
        self.condition_map[name] = node_id
        return node_id

    def add_mentions_edge(self, paper_id: int, treatment_id: int):
        """Insert MENTIONS edge"""
        sql = "INSERT INTO mentions_edges (from_node_id, to_node_id) VALUES (:1, :2)"
        self.cursor.execute(sql, [paper_id, treatment_id])
        self.stats['mentions_edges'] += 1

    def add_treats_edge(self, treatment_id: int, condition_id: int):
        """Insert TREATS edge"""
        # Check exist to avoid dupes (since logical graph might have dupes)
        sql_check = "SELECT 1 FROM treats_edges WHERE from_node_id=:1 AND to_node_id=:2"
        self.cursor.execute(sql_check, [treatment_id, condition_id])
        if self.cursor.fetchone():
            return

        sql = "INSERT INTO treats_edges (from_node_id, to_node_id) VALUES (:1, :2)"
        self.cursor.execute(sql, [treatment_id, condition_id])
        self.stats['treats_edges'] += 1

    def build_graph_from_entities(
        self,
        paper_filename: str,
        paper_title: str,
        treatments: Set[str],
        conditions: Set[str],
        relationships: List[Tuple[str, str]],
        publication_date: str = None,
        paper_embedding: List[float] = None,
        treatment_embeddings: Dict[str, List[float]] = None,
        condition_embeddings: Dict[str, List[float]] = None
    ):
        """Main orchestrator"""
        
        # 1. Paper
        paper_id = self.add_paper(paper_filename, paper_title, publication_date, paper_embedding)
        
        # 2. Treatments + Mentions
        treatment_embeddings = treatment_embeddings or {}
        for t_name in treatments:
            t_emb = treatment_embeddings.get(t_name)
            t_id = self.add_treatment(t_name, embedding=t_emb)
            self.add_mentions_edge(paper_id, t_id)
            
        # 3. Conditions
        condition_embeddings = condition_embeddings or {}
        for c_name in conditions:
            c_emb = condition_embeddings.get(c_name)
            self.add_condition(c_name, embedding=c_emb)
            
        # 4. Treats Edges
        for t_name, c_name in relationships:
            if t_name in self.treatment_map and c_name in self.condition_map:
                t_id = self.treatment_map[t_name]
                c_id = self.condition_map[c_name]
                self.add_treats_edge(t_id, c_id)

    def print_summary(self):
        print("\n📊 Database Load Summary:")
        print(f"   ✓ Papers added: {self.stats['papers']}")
        print(f"   ✓ Treatments added: {self.stats['treatments']}")
        print(f"   ✓ Conditions added: {self.stats['conditions']}")
        print(f"   ✓ MENTIONS edges: {self.stats['mentions_edges']}")
        print(f"   ✓ TREATS edges: {self.stats['treats_edges']}")
