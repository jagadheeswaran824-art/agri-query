"""
KrishiSahay Database Seeder
Populate database with sample agricultural data
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
import random
from database_manager import DatabaseManager, DatabaseConfig, KnowledgeManager

class DatabaseSeeder:
    """Seed database with comprehensive agricultural data"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.knowledge_manager = KnowledgeManager(db_manager)
    
    async def seed_all(self):
        """Seed all data"""
        print("🌱 Starting database seeding...")
        
        await self.seed_crops()
        await self.seed_diseases()
        await self.seed_pests()
        await self.seed_fertilizers()
        await self.seed_government_schemes()
        await self.seed_sample_users()
        await self.seed_expert_knowledge()
        await self.seed_weather_data()
        await self.seed_market_prices()
        
        print("✅ Database seeding completed!")
    
    async def seed_crops(self):
        """Seed crop data"""
        print("🌾 Seeding crops...")
        
        crops_data = [
            {
                'name': 'Wheat',
                'scientific_name': 'Triticum aestivum',
                'category': 'Cereal',
                'subcategory': 'Grain',
                'growing_season': 'Rabi',
                'climate_requirements': {
                    'temperature_range': '15-25°C',
                    'rainfall': '300-400mm',
                    'humidity': '50-70%'
                },
                'soil_requirements': {
                    'type': 'Well-drained loamy soil',
                    'ph_range': '6.0-7.5',
                    'organic_matter': 'Medium to high'
                },
                'water_requirements': {
                    'irrigation_frequency': '7-10 days',
                    'critical_stages': ['tillering', 'flowering', 'grain_filling']
                },
                'growth_stages': {
                    'germination': '7-10 days',
                    'tillering': '30-45 days',
                    'flowering': '90-100 days',
                    'maturity': '120-150 days'
                },
                'nutritional_needs': {
                    'nitrogen': '120-150 kg/ha',
                    'phosphorus': '60-80 kg/ha',
                    'potassium': '40-60 kg/ha'
                },
                'common_diseases': ['rust', 'blight', 'smut'],
                'common_pests': ['aphids', 'termites', 'army_worm'],
                'companion_crops': ['mustard', 'gram', 'pea'],
                'market_info': {
                    'msp_2023': '2125 per quintal',
                    'export_potential': 'High',
                    'storage_period': '12-18 months'
                }
            },
            {
                'name': 'Rice',
                'scientific_name': 'Oryza sativa',
                'category': 'Cereal',
                'subcategory': 'Grain',
                'growing_season': 'Kharif',
                'climate_requirements': {
                    'temperature_range': '20-35°C',
                    'rainfall': '1000-2000mm',
                    'humidity': '80-90%'
                },
                'soil_requirements': {
                    'type': 'Clay or clay loam',
                    'ph_range': '5.5-7.0',
                    'water_retention': 'High'
                },
                'water_requirements': {
                    'irrigation_method': 'Flooding',
                    'water_depth': '5-10 cm',
                    'drainage_before_harvest': '15-20 days'
                },
                'growth_stages': {
                    'germination': '5-7 days',
                    'tillering': '25-35 days',
                    'flowering': '80-90 days',
                    'maturity': '110-140 days'
                },
                'nutritional_needs': {
                    'nitrogen': '100-120 kg/ha',
                    'phosphorus': '50-60 kg/ha',
                    'potassium': '50-60 kg/ha'
                },
                'common_diseases': ['blast', 'bacterial_blight', 'sheath_blight'],
                'common_pests': ['stem_borer', 'brown_planthopper', 'gall_midge'],
                'companion_crops': ['fish_farming', 'duck_farming'],
                'market_info': {
                    'msp_2023': '2183 per quintal',
                    'export_potential': 'Very High',
                    'varieties': ['Basmati', 'Non-Basmati']
                }
            },
            {
                'name': 'Mustard',
                'scientific_name': 'Brassica juncea',
                'category': 'Oilseed',
                'subcategory': 'Edible Oil',
                'growing_season': 'Rabi',
                'climate_requirements': {
                    'temperature_range': '10-25°C',
                    'rainfall': '200-400mm',
                    'humidity': '60-70%'
                },
                'soil_requirements': {
                    'type': 'Well-drained sandy loam',
                    'ph_range': '6.0-7.5',
                    'salinity_tolerance': 'Moderate'
                },
                'water_requirements': {
                    'irrigation_frequency': '15-20 days',
                    'critical_stages': ['flowering', 'pod_formation']
                },
                'growth_stages': {
                    'germination': '4-6 days',
                    'flowering': '45-60 days',
                    'pod_formation': '70-80 days',
                    'maturity': '90-120 days'
                },
                'nutritional_needs': {
                    'nitrogen': '80-100 kg/ha',
                    'phosphorus': '40-50 kg/ha',
                    'potassium': '20-30 kg/ha'
                },
                'common_diseases': ['white_rust', 'downy_mildew', 'alternaria_blight'],
                'common_pests': ['aphids', 'flea_beetle', 'mustard_sawfly'],
                'companion_crops': ['wheat', 'barley', 'gram'],
                'market_info': {
                    'msp_2023': '5450 per quintal',
                    'oil_content': '38-42%',
                    'industrial_use': 'Biodiesel production'
                }
            }
        ]
        
        for crop_data in crops_data:
            crop_id = await self.knowledge_manager.add_crop(crop_data)
            print(f"  ✅ Added crop: {crop_data['name']} ({crop_id})")
    
    async def seed_diseases(self):
        """Seed disease data"""
        print("🦠 Seeding diseases...")
        
        diseases_data = [
            {
                'name': 'Wheat Rust',
                'scientific_name': 'Puccinia triticina',
                'type': 'fungal',
                'symptoms': {
                    'leaf_symptoms': 'Orange-red pustules on leaves',
                    'stem_symptoms': 'Dark brown pustules on stems',
                    'severity': 'Can cause 10-70% yield loss'
                },
                'causes': {
                    'pathogen': 'Puccinia triticina fungus',
                    'favorable_conditions': 'High humidity, moderate temperature',
                    'spread': 'Wind-borne spores'
                },
                'prevention_methods': {
                    'resistant_varieties': ['HD-2967', 'PBW-343', 'DBW-88'],
                    'cultural_practices': 'Crop rotation, field sanitation',
                    'monitoring': 'Regular field inspection'
                },
                'treatment_options': {
                    'fungicides': ['Propiconazole', 'Tebuconazole'],
                    'application_timing': 'At first appearance of symptoms',
                    'organic_options': ['Neem oil', 'Copper fungicides']
                }
            },
            {
                'name': 'Rice Blast',
                'scientific_name': 'Magnaporthe oryzae',
                'type': 'fungal',
                'symptoms': {
                    'leaf_blast': 'Diamond-shaped lesions with gray centers',
                    'neck_blast': 'Brown lesions at panicle neck',
                    'panicle_blast': 'Entire panicle becomes white'
                },
                'causes': {
                    'pathogen': 'Magnaporthe oryzae fungus',
                    'favorable_conditions': 'High humidity, nitrogen excess',
                    'spread': 'Airborne spores, infected seeds'
                },
                'prevention_methods': {
                    'resistant_varieties': ['Pusa-1121', 'CSR-30', 'Improved Samba Mahsuri'],
                    'seed_treatment': 'Carbendazim or Tricyclazole',
                    'balanced_nutrition': 'Avoid excess nitrogen'
                },
                'treatment_options': {
                    'fungicides': ['Tricyclazole', 'Carbendazim', 'Azoxystrobin'],
                    'application_method': 'Foliar spray',
                    'frequency': '2-3 applications at 15-day intervals'
                }
            }
        ]
        
        async with self.db.get_connection() as conn:
            for disease_data in diseases_data:
                disease_id = str(uuid.uuid4())
                await conn.execute("""
                    INSERT INTO diseases (id, name, scientific_name, type, symptoms,
                                        causes, prevention_methods, treatment_options)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                    disease_id,
                    disease_data['name'],
                    disease_data['scientific_name'],
                    disease_data['type'],
                    json.dumps(disease_data['symptoms']),
                    json.dumps(disease_data['causes']),
                    json.dumps(disease_data['prevention_methods']),
                    json.dumps(disease_data['treatment_options'])
                )
                print(f"  ✅ Added disease: {disease_data['name']}")
    
    async def seed_government_schemes(self):
        """Seed government schemes"""
        print("🏛️ Seeding government schemes...")
        
        schemes_data = [
            {
                'scheme_name': 'PM Kisan Samman Nidhi',
                'scheme_code': 'PM-KISAN',
                'description': 'Income support scheme for small and marginal farmers',
                'eligibility_criteria': {
                    'land_holding': 'Up to 2 hectares',
                    'farmer_type': 'Small and marginal farmers',
                    'exclusions': ['Income tax payers', 'Government employees']
                },
                'benefits': {
                    'amount': '₹6000 per year',
                    'installments': '3 installments of ₹2000 each',
                    'payment_mode': 'Direct bank transfer'
                },
                'application_process': {
                    'online': 'pmkisan.gov.in',
                    'offline': 'Village Revenue Officer',
                    'documents': ['Aadhaar', 'Land records', 'Bank details']
                },
                'required_documents': [
                    'Aadhaar Card',
                    'Land ownership documents',
                    'Bank account details',
                    'Mobile number'
                ],
                'states_applicable': ['All States and UTs'],
                'target_beneficiaries': ['Small farmers', 'Marginal farmers'],
                'budget_allocation': 75000.00,
                'launch_date': '2019-02-24',
                'status': 'active',
                'website_url': 'https://pmkisan.gov.in'
            },
            {
                'scheme_name': 'Pradhan Mantri Fasal Bima Yojana',
                'scheme_code': 'PMFBY',
                'description': 'Crop insurance scheme to protect farmers against crop losses',
                'eligibility_criteria': {
                    'farmer_type': 'All farmers including sharecroppers and tenant farmers',
                    'crops_covered': 'Food crops, oilseeds, annual commercial/horticultural crops'
                },
                'benefits': {
                    'coverage': 'Pre-sowing to post-harvest losses',
                    'premium_subsidy': 'Up to 90% premium subsidy',
                    'claim_settlement': 'Technology-based assessment'
                },
                'application_process': {
                    'online': 'pmfby.gov.in',
                    'offline': 'Bank branches, CSCs',
                    'timeline': 'Before sowing season'
                },
                'required_documents': [
                    'Aadhaar Card',
                    'Land records',
                    'Bank account details',
                    'Sowing certificate'
                ],
                'states_applicable': ['All States'],
                'target_beneficiaries': ['All farmers'],
                'budget_allocation': 15695.00,
                'launch_date': '2016-01-13',
                'status': 'active',
                'website_url': 'https://pmfby.gov.in'
            }
        ]
        
        async with self.db.get_connection() as conn:
            for scheme_data in schemes_data:
                scheme_id = str(uuid.uuid4())
                await conn.execute("""
                    INSERT INTO government_schemes (id, scheme_name, scheme_code, description,
                                                  eligibility_criteria, benefits, application_process,
                                                  required_documents, states_applicable,
                                                  target_beneficiaries, budget_allocation,
                                                  launch_date, status, website_url)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                """,
                    scheme_id,
                    scheme_data['scheme_name'],
                    scheme_data['scheme_code'],
                    scheme_data['description'],
                    json.dumps(scheme_data['eligibility_criteria']),
                    json.dumps(scheme_data['benefits']),
                    json.dumps(scheme_data['application_process']),
                    scheme_data['required_documents'],
                    scheme_data['states_applicable'],
                    scheme_data['target_beneficiaries'],
                    scheme_data['budget_allocation'],
                    scheme_data['launch_date'],
                    scheme_data['status'],
                    scheme_data['website_url']
                )
                print(f"  ✅ Added scheme: {scheme_data['scheme_name']}")
    
    async def seed_sample_users(self):
        """Seed sample users"""
        print("👥 Seeding sample users...")
        
        sample_users = [
            {
                'username': 'farmer_raj',
                'email': 'raj.farmer@example.com',
                'phone': '+91-9876543210',
                'password_hash': 'hashed_password_123',
                'user_type': 'farmer',
                'profile_data': {
                    'full_name': 'Raj Kumar',
                    'age': 45,
                    'experience_years': 20
                },
                'latitude': 28.6139,
                'longitude': 77.2090
            },
            {
                'username': 'expert_sharma',
                'email': 'dr.sharma@agri.gov.in',
                'phone': '+91-9876543211',
                'password_hash': 'hashed_password_456',
                'user_type': 'expert',
                'profile_data': {
                    'full_name': 'Dr. Priya Sharma',
                    'qualification': 'PhD in Plant Pathology',
                    'specialization': 'Crop Diseases'
                },
                'latitude': 28.7041,
                'longitude': 77.1025
            }
        ]
        
        async with self.db.get_connection() as conn:
            for user_data in sample_users:
                user_id = str(uuid.uuid4())
                await conn.execute("""
                    INSERT INTO users (id, username, email, phone, password_hash,
                                     user_type, profile_data, location, is_active)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, ST_Point($8, $9), true)
                """,
                    user_id,
                    user_data['username'],
                    user_data['email'],
                    user_data['phone'],
                    user_data['password_hash'],
                    user_data['user_type'],
                    json.dumps(user_data['profile_data']),
                    user_data['longitude'],
                    user_data['latitude']
                )
                print(f"  ✅ Added user: {user_data['username']}")

async def main():
    """Run database seeding"""
    config = DatabaseConfig()
    db_manager = DatabaseManager(config)
    await db_manager.initialize_pool()
    
    seeder = DatabaseSeeder(db_manager)
    await seeder.seed_all()
    
    await db_manager.pool.close()

if __name__ == "__main__":
    asyncio.run(main())