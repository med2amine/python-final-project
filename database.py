import sqlite3
import json


class DatabaseManager:
    def __init__(self, db_path="stats_calc.db"):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        """Create all database tables"""
        cursor = self.connection.cursor()

        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS datasets (
                dataset_id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_path TEXT,
                upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                row_count INTEGER,
                column_count INTEGER,
                columns_names TEXT,
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS analysis_history (
                analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id INTEGER,
                analysis_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                analysis_name TEXT,
                calculations_performed TEXT,
                results_summary TEXT,
                FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id)
            );

            CREATE TABLE IF NOT EXISTS calculation_results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                column_name TEXT,
                calculation_type TEXT,
                result_value REAL,
                FOREIGN KEY (analysis_id) REFERENCES analysis_history(analysis_id)
            );

            CREATE TABLE IF NOT EXISTS user_preferences (
                preference_id INTEGER PRIMARY KEY AUTOINCREMENT,
                preference_key TEXT UNIQUE,
                preference_value TEXT
            );
        ''')
        self.connection.commit()

    def register_dataset(self, filename, filepath, dataframe):
        """Save dataset metadata when file is loaded"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO datasets (filename, file_path, row_count, column_count, columns_names)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                filename,
                filepath,
                len(dataframe),
                len(dataframe.columns),
                json.dumps(dataframe.columns.tolist())
            ))
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error registering dataset: {e}")
            self.connection.rollback()
            return None

    def _convert_to_serializable(self, obj):
        """Convert numpy/pandas types to JSON-serializable Python types"""
        if isinstance(obj, dict):
            return {k: self._convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_serializable(item) for item in obj]
        elif hasattr(obj, 'item'):  # numpy types (float64, int64, etc.)
            return obj.item()
        elif hasattr(obj, 'tolist'):  # numpy arrays
            return obj.tolist()
        return obj

    def save_analysis(self, dataset_id, analysis_name, calculations, results):
        """Save analysis results to database"""
        try:
            cursor = self.connection.cursor()

            # Convert to JSON-serializable format
            calculations_clean = self._convert_to_serializable(calculations)
            results_clean = self._convert_to_serializable(results)

            # Save to analysis_history
            cursor.execute('''
                INSERT INTO analysis_history 
                (dataset_id, analysis_name, calculations_performed, results_summary)
                VALUES (?, ?, ?, ?)
            ''', (
                dataset_id,
                analysis_name,
                json.dumps(calculations_clean),
                json.dumps(results_clean)
            ))

            analysis_id = cursor.lastrowid

            # Save detailed results
            # Handle both nested and flat result structures
            for key, value in results_clean.items():
                if isinstance(value, dict):
                    # Nested: results = {'col1': {'mean': 5, 'std': 2}}
                    for calc_type, calc_value in value.items():
                        cursor.execute('''
                            INSERT INTO calculation_results
                            (analysis_id, column_name, calculation_type, result_value)
                            VALUES (?, ?, ?, ?)
                        ''', (analysis_id, key, calc_type, float(calc_value)))
                else:
                    # Flat: results = {'mean': 5, 'std': 2}
                    cursor.execute('''
                        INSERT INTO calculation_results
                        (analysis_id, column_name, calculation_type, result_value)
                        VALUES (?, ?, ?, ?)
                    ''', (analysis_id, 'overall', key, float(value)))

            self.connection.commit()
            return analysis_id

        except sqlite3.Error as e:
            print(f"Error saving analysis: {e}")
            self.connection.rollback()
            return None
        except (ValueError, TypeError) as e:
            print(f"Error converting data: {e}")
            self.connection.rollback()
            return None

    def get_analysis_history(self, limit=50):
        """Retrieve recent analyses"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT 
                    ah.analysis_id,
                    ah.analysis_name,
                    ah.analysis_date,
                    d.filename,
                    ah.calculations_performed
                FROM analysis_history ah
                JOIN datasets d ON ah.dataset_id = d.dataset_id
                ORDER BY ah.analysis_date DESC
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving history: {e}")
            return []

    def get_dataset_info(self, dataset_id):
        """Get info about a specific dataset"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT * FROM datasets WHERE dataset_id = ?', (dataset_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error retrieving dataset info: {e}")
            return None

    def get_analysis_details(self, analysis_id):
        """Get detailed results of a specific analysis"""
        try:
            cursor = self.connection.cursor()

            # Get analysis info
            cursor.execute('''
                SELECT ah.*, d.filename
                FROM analysis_history ah
                JOIN datasets d ON ah.dataset_id = d.dataset_id
                WHERE ah.analysis_id = ?
            ''', (analysis_id,))
            analysis_info = cursor.fetchone()

            # Get calculation results
            cursor.execute('''
                SELECT column_name, calculation_type, result_value
                FROM calculation_results
                WHERE analysis_id = ?
            ''', (analysis_id,))
            calc_results = cursor.fetchall()

            return {
                'info': analysis_info,
                'results': calc_results
            }
        except sqlite3.Error as e:
            print(f"Error retrieving analysis details: {e}")
            return None

    def delete_analysis(self, analysis_id):
        """Delete an analysis and its results"""
        try:
            cursor = self.connection.cursor()

            # Delete calculation results first (foreign key constraint)
            cursor.execute('DELETE FROM calculation_results WHERE analysis_id = ?', (analysis_id,))

            # Delete analysis
            cursor.execute('DELETE FROM analysis_history WHERE analysis_id = ?', (analysis_id,))

            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting analysis: {e}")
            self.connection.rollback()
            return False

    def get_all_datasets(self):
        """Get list of all datasets"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT dataset_id, filename, upload_date, row_count, column_count
                FROM datasets
                ORDER BY upload_date DESC
            ''')
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving datasets: {e}")
            return []

    def save_preference(self, key, value):
        """Save user preference"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO user_preferences (preference_key, preference_value)
                VALUES (?, ?)
            ''', (key, value))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error saving preference: {e}")
            return False

    def get_preference(self, key, default=None):
        """Get user preference"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT preference_value FROM user_preferences WHERE preference_key = ?', (key,))
            result = cursor.fetchone()
            return result[0] if result else default
        except sqlite3.Error as e:
            print(f"Error retrieving preference: {e}")
            return default

    def close(self):
        """Close database connection"""
        self.connection.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically close connection"""
        self.close()