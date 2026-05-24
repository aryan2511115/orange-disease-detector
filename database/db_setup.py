"""
Database Configuration and Setup Module
Creates and manages MySQL database tables for orange disease detection system
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime
import json
import os

class DatabaseManager:
    """
    Manages database connections and operations for the orange disease detection system.
    """
    
    def __init__(self, host='localhost', user='root', password='', database='orange_disease_db'):
        """
        Initialize database manager.
        
        Args:
            host (str): Database host
            user (str): Database user
            password (str): Database password
            database (str): Database name
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
    
    def connect(self):
        """
        Establish connection to MySQL database.
        
        Returns:
            bool: Connection status
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            print("✓ Connected to MySQL server")
            return True
        except Error as e:
            print(f"✗ Error connecting to MySQL: {e}")
            return False
    
    def create_database(self):
        """
        Create the orange disease database if it doesn't exist.
        """
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            print(f"✓ Database '{self.database}' ready")
            cursor.close()
            
            # Reconnect to the new database
            self.connection.close()
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print(f"✓ Connected to database '{self.database}'")
        except Error as e:
            print(f"✗ Error creating database: {e}")
    
    def create_users_table(self):
        """
        Create users table for storing user information.
        """
        if not self.connection:
            self.connect()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(150),
            profile_picture VARCHAR(255),
            language_preference VARCHAR(10) DEFAULT 'en',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_query)
            self.connection.commit()
            print("✓ Users table created successfully")
            cursor.close()
        except Error as e:
            print(f"✗ Error creating users table: {e}")
    
    def create_predictions_table(self):
        """
        Create predictions table for storing prediction history.
        """
        if not self.connection:
            self.connect()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS predictions (
            prediction_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            image_name VARCHAR(255) NOT NULL,
            image_path VARCHAR(500),
            predicted_disease VARCHAR(100) NOT NULL,
            confidence_score FLOAT NOT NULL,
            disease_severity FLOAT,
            prediction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            gradcam_path VARCHAR(500),
            model_used VARCHAR(50),
            
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_disease (predicted_disease),
            INDEX idx_timestamp (prediction_timestamp)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_query)
            self.connection.commit()
            print("✓ Predictions table created successfully")
            cursor.close()
        except Error as e:
            print(f"✗ Error creating predictions table: {e}")
    
    def create_disease_info_table(self):
        """
        Create disease information table.
        """
        if not self.connection:
            self.connect()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS disease_info (
            disease_id INT AUTO_INCREMENT PRIMARY KEY,
            disease_name VARCHAR(100) UNIQUE NOT NULL,
            disease_name_hi VARCHAR(100),
            disease_name_mr VARCHAR(100),
            description TEXT,
            description_hi TEXT,
            description_mr TEXT,
            symptoms TEXT,
            symptoms_hi TEXT,
            symptoms_mr TEXT,
            treatment TEXT,
            treatment_hi TEXT,
            treatment_mr TEXT,
            prevention TEXT,
            prevention_hi TEXT,
            prevention_mr TEXT,
            fertilizer_recommendation TEXT,
            fertilizer_recommendation_hi TEXT,
            fertilizer_recommendation_mr TEXT,
            severity_impact VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_query)
            self.connection.commit()
            print("✓ Disease Info table created successfully")
            cursor.close()
        except Error as e:
            print(f"✗ Error creating disease_info table: {e}")
    
    def insert_disease_data(self):
        """
        Insert default disease information into the database.
        """
        if not self.connection:
            self.connect()
        
        diseases = [
            {
                'disease_name': 'Citrus Canker',
                'disease_name_hi': 'साइट्रस कैंकर',
                'disease_name_mr': 'साइट्रस कॅन्कर',
                'description': 'A bacterial disease caused by Xanthomonas citri that causes lesions on fruit, leaves, and twigs.',
                'description_hi': 'एक जीवाणु रोग जो फलों, पत्तियों और टहनियों पर घाव पैदा करता है।',
                'description_mr': 'एक बैक्टेरिया रोग जो फले, पत्ते आणि टहनीवर जखम निर्माण करतो।',
                'symptoms': 'Water-soaked lesions with yellow halos on leaves and fruit, leaf yellowing and drop, defoliation.',
                'symptoms_hi': 'पत्तियों और फलों पर पीले रंग के प्रभामंडल के साथ पानी से भरे घाव।',
                'symptoms_mr': 'पत्ते आणि फलांवर पिवळ्या रंगाच्या प्रभामंडलासह पाणी भरलेले जखम।',
                'treatment': 'Prune affected branches, apply copper fungicides, maintain tree vigor, improve drainage.',
                'treatment_hi': 'प्रभावित शाखाओं को काटें, कॉपर कवकनाशी लागू करें।',
                'treatment_mr': 'प्रभावित शाखा कापा, कॉपर फंजिसाइड लागू करा।',
                'prevention': 'Remove infected trees, use disease-free nursery stock, maintain good sanitation.',
                'prevention_hi': 'संक्रमित पेड़ों को हटाएं, स्वस्थ नर्सरी स्टॉक का उपयोग करें।',
                'prevention_mr': 'संक्रमित झाड हटवा, निरोगी नर्सरी स्टॉक वापरा।',
                'fertilizer_recommendation': 'Apply balanced NPK (10-10-10) fertilizer with micronutrients. Focus on nitrogen for tree vigor.',
                'fertilizer_recommendation_hi': 'संतुलित NPK खाद लागू करें और पेड़ की मजबूती बढ़ाएं।',
                'fertilizer_recommendation_mr': 'संतुलित NPK खत लागू करा आणि झाडाची सामर्थ्य वाढवा।',
                'severity_impact': 'High'
            },
            {
                'disease_name': 'Black Spot',
                'disease_name_hi': 'काला धब्बा',
                'disease_name_mr': 'काळा डाग',
                'description': 'A fungal disease caused by Phyllosticta citricarpa, causing black circular spots on fruit and leaves.',
                'description_hi': 'एक फंगल रोग जो फलों और पत्तियों पर काले गोलाकार धब्बे पैदा करता है।',
                'description_mr': 'एक बोलीविद रोग जो फले आणि पत्ते वर काळे गोलाकार डाग निर्माण करतो।',
                'symptoms': 'Small black spots on fruit starting near the calyx, gradual expansion, yellow halo development.',
                'symptoms_hi': 'फलों पर काले धब्बे जो धीरे-धीरे बढ़ते हैं।',
                'symptoms_mr': 'फलांवर काळे डाग जे हळूहळू वाढतात।',
                'treatment': 'Apply copper-based fungicides, remove infected fruit, improve air circulation.',
                'treatment_hi': 'कॉपर आधारित कवकनाशी लागू करें और संक्रमित फलों को हटाएं।',
                'treatment_mr': 'कॉपर आधारित बोलीविदनाशक लागू करा आणि संक्रमित फले हटवा।',
                'prevention': 'Proper pruning for air circulation, remove fallen fruit, apply preventive fungicides.',
                'prevention_hi': 'उचित छंटाई करें, गिरे हुए फलों को हटाएं, रोकथाम कवकनाशी लागू करें।',
                'prevention_mr': 'योग्य छाटणी करा, पडलेले फले हटवा, प्रतिरोधक बोलीविदनाशक लागू करा।',
                'fertilizer_recommendation': 'Use potassium-rich fertilizers (NPK 10-10-30) to improve fruit resistance.',
                'fertilizer_recommendation_hi': 'पोटेशियम से भरपूर खाद का उपयोग करें।',
                'fertilizer_recommendation_mr': 'पोटेशियम समृद्ध खत वापरा।',
                'severity_impact': 'Medium'
            },
            {
                'disease_name': 'Citrus Greening (HLB)',
                'disease_name_hi': 'साइट्रस ग्रीनिंग',
                'disease_name_mr': 'साइट्रस ग्रीनिंग',
                'description': 'A serious bacterial disease transmitted by psyllid insects, causing yellowing of leaves and small bitter fruit.',
                'description_hi': 'एक गंभीर बैक्टीरियल रोग जो साइलिड कीटों द्वारा प्रसारित होता है।',
                'description_mr': 'एक गंभीर बॅक्टेरिया रोग जो साइलिड कीटांनी प्रसारित होतो।',
                'symptoms': 'Asymmetrical yellow blotches on leaves, small misshapen fruit, decline in tree vigor.',
                'symptoms_hi': 'पत्तियों पर असमान पीले धब्बे, छोटे विकृत फल, पेड़ की शक्ति में गिरावट।',
                'symptoms_mr': 'पत्ते वर असमान पिवळे डाग, लहान विकृत फले, झाडाची शक्ती कमी होणे।',
                'treatment': 'No cure exists, remove infected trees, control psyllid vector with insecticides.',
                'treatment_hi': 'कोई इलाज नहीं है, संक्रमित पेड़ों को हटाएं, कीटनाशकों से नियंत्रण करें।',
                'treatment_mr': 'कोणतेही उपचार नाही, संक्रमित झाड हटवा, कीटकनाशकांनी नियंत्रण करा।',
                'prevention': 'Plant certified disease-free trees, control psyllid with insecticides, remove infected trees.',
                'prevention_hi': 'प्रमाणित रोगमुक्त पेड़ लगाएं, साइलिड को कीटनाशकों से नियंत्रित करें।',
                'prevention_mr': 'प्रमाणित रोगमुक्त झाड लावा, साइलिड ला कीटकनाशकांनी नियंत्रण करा।',
                'fertilizer_recommendation': 'Apply high nitrogen fertilizers (NPK 16-16-16) to support tree health before removal.',
                'fertilizer_recommendation_hi': 'उच्च नाइट्रोजन खाद लागू करें।',
                'fertilizer_recommendation_mr': 'उच्च नायट्रोजन खत लागू करा।',
                'severity_impact': 'Critical'
            },
            {
                'disease_name': 'Leaf Miner',
                'disease_name_hi': 'पत्ती माइनर',
                'disease_name_mr': 'पत्री खनक',
                'description': 'An insect pest that mines through citrus leaves, creating white or brown serpentine trails.',
                'description_hi': 'एक कीट जो साइट्रस पत्तियों में सुरंग बनाता है, सफेद या भूरे रंग के निशान बनाता है।',
                'description_mr': 'एक कीट जो साइट्रस पत्ते मध्ये सुरंग बनवतो, पांढरे किंवा तपकिरी रंगाचे खुणा बनवतो।',
                'symptoms': 'Meandering mines on leaves, leaf yellowing, premature leaf drop, reduced photosynthesis.',
                'symptoms_hi': 'पत्तियों पर मेंडरिंग खदानें, पत्तियों का पीलापन, पत्तियों का समय से पहले गिरना।',
                'symptoms_mr': 'पत्ते वर मेंडरिंग खदाने, पत्ते पिवळे होणे, पत्ते वेळोवेळी पडणे।',
                'treatment': 'Apply insecticides (neem oil, pyrethrin), prune affected leaves, maintain tree vigor.',
                'treatment_hi': 'कीटनाशक लागू करें, प्रभावित पत्तियों को काटें, पेड़ की मजबूती बनाए रखें।',
                'treatment_mr': 'कीटकनाशक लागू करा, प्रभावित पत्ते कापा, झाडाची मजबूती राखा।',
                'prevention': 'Regular inspection, maintain good canopy health, use parasitic wasps, avoid excessive nitrogen.',
                'prevention_hi': 'नियमित निरीक्षण, छत्र स्वास्थ्य बनाए रखें, परजीवी ततैया का उपयोग करें।',
                'prevention_mr': 'नियमित तपासणी, छत्र आरोग्य राखा, परजीवी तेंड्यांचा वापर करा।',
                'fertilizer_recommendation': 'Apply balanced fertilizers with micronutrients, avoid excess nitrogen which attracts pests.',
                'fertilizer_recommendation_hi': 'संतुलित खाद लागू करें, अतिरिक्त नाइट्रोजन से बचें।',
                'fertilizer_recommendation_mr': 'संतुलित खत लागू करा, अतिरिक्त नायट्रोजन टाळा।',
                'severity_impact': 'Low to Medium'
            },
            {
                'disease_name': 'Healthy Orange Leaf',
                'disease_name_hi': 'स्वस्थ संतरे की पत्ती',
                'disease_name_mr': 'निरोगी संत्र्याचे पत्र',
                'description': 'Healthy citrus leaves showing no signs of disease or pest damage.',
                'description_hi': 'स्वस्थ साइट्रस पत्तियां जो कोई रोग या कीट क्षति नहीं दिखाती हैं।',
                'description_mr': 'निरोगी साइट्रस पत्र जे कोणतेही रोग किंवा कीट नुकसान दर्शवत नाहीत।',
                'symptoms': 'Green color, smooth surface, no spots or lesions, vigorous growth.',
                'symptoms_hi': 'हरा रंग, चिकनी सतह, कोई धब्बे या घाव नहीं, जोरदार वृद्धि।',
                'symptoms_mr': 'हिरवा रंग, गुळगुळीत पृष्ठभाग, कोणतेही डाग किंवा जखम नाही, जोरदार वृद्धि।',
                'treatment': 'No treatment needed, maintain regular care and nutrition.',
                'treatment_hi': 'कोई इलाज की आवश्यकता नहीं है, नियमित देखभाल और पोषण बनाए रखें।',
                'treatment_mr': 'कोणतेही उपचार आवश्यक नाही, नियमित काळजी आणि पोषण राखा।',
                'prevention': 'Regular monitoring, proper irrigation, balanced fertilization, pest management.',
                'prevention_hi': 'नियमित निगरानी, उचित सिंचाई, संतुलित पोषण, कीट प्रबंधन।',
                'prevention_mr': 'नियमित निरीक्षण, योग्य सिंचन, संतुलित पोषण, कीट व्यवस्थापन।',
                'fertilizer_recommendation': 'Maintain balanced NPK (10-10-10) with micronutrients, ensure proper pH.',
                'fertilizer_recommendation_hi': 'संतुलित NPK खाद बनाए रखें, उचित pH सुनिश्चित करें।',
                'fertilizer_recommendation_mr': 'संतुलित NPK खत राखा, योग्य pH सुनिश्चित करा।',
                'severity_impact': 'None'
            }
        ]
        
        try:
            cursor = self.connection.cursor()
            
            # Check if data already exists
            cursor.execute("SELECT COUNT(*) FROM disease_info")
            if cursor.fetchone()[0] == 0:
                for disease in diseases:
                    insert_query = """
                    INSERT INTO disease_info (
                        disease_name, disease_name_hi, disease_name_mr,
                        description, description_hi, description_mr,
                        symptoms, symptoms_hi, symptoms_mr,
                        treatment, treatment_hi, treatment_mr,
                        prevention, prevention_hi, prevention_mr,
                        fertilizer_recommendation, fertilizer_recommendation_hi, fertilizer_recommendation_mr,
                        severity_impact
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    values = (
                        disease['disease_name'],
                        disease.get('disease_name_hi', ''),
                        disease.get('disease_name_mr', ''),
                        disease.get('description', ''),
                        disease.get('description_hi', ''),
                        disease.get('description_mr', ''),
                        disease.get('symptoms', ''),
                        disease.get('symptoms_hi', ''),
                        disease.get('symptoms_mr', ''),
                        disease.get('treatment', ''),
                        disease.get('treatment_hi', ''),
                        disease.get('treatment_mr', ''),
                        disease.get('prevention', ''),
                        disease.get('prevention_hi', ''),
                        disease.get('prevention_mr', ''),
                        disease.get('fertilizer_recommendation', ''),
                        disease.get('fertilizer_recommendation_hi', ''),
                        disease.get('fertilizer_recommendation_mr', ''),
                        disease.get('severity_impact', '')
                    )
                    
                    cursor.execute(insert_query, values)
                
                self.connection.commit()
                print(f"✓ Inserted {len(diseases)} disease records into database")
            else:
                print("✓ Disease data already exists in database")
            
            cursor.close()
        except Error as e:
            print(f"✗ Error inserting disease data: {e}")
    
    def initialize_database(self):
        """
        Complete database initialization pipeline.
        """
        print("\n" + "="*60)
        print("DATABASE INITIALIZATION")
        print("="*60 + "\n")
        
        if not self.connect():
            return False
        
        self.create_database()
        self.create_users_table()
        self.create_predictions_table()
        self.create_disease_info_table()
        self.insert_disease_data()
        
        print("\n✓ Database initialization completed successfully!")
        
        return True
    
    def close_connection(self):
        """
        Close database connection.
        """
        if self.connection:
            self.connection.close()
            print("Database connection closed")


def main():
    """
    Example database setup.
    """
    db_manager = DatabaseManager(
        host='localhost',
        user='root',
        password='',  # Update with your MySQL password
        database='orange_disease_db'
    )
    
    db_manager.initialize_database()
    db_manager.close_connection()


if __name__ == '__main__':
    main()
