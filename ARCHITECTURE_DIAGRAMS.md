# System Architecture & Diagrams
## Orange Disease Detection System

## 1. System Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                               │
│  Web Browser (Desktop/Mobile)                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  HTML5 / CSS3 / JavaScript                                  │ │
│  │  - Home Page                                                │ │
│  │  - Detection Interface                                      │ │
│  │  - About & Contact Pages                                   │ │
│  │  - Multilingual Support (EN/HI/MR)                         │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
                            │
                REST API (CORS Enabled)
                    HTTP/HTTPS
                            │
┌────────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                             │
│  Flask Web Framework (Python)                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  REST API Endpoints:                                        │ │
│  │  - POST   /api/predict                                      │ │
│  │  - GET    /api/diseases                                     │ │
│  │  - GET    /api/disease-info/<name>                          │ │
│  │  - GET    /api/prediction-history/<user_id>                 │ │
│  │  - GET    /api/statistics                                   │ │
│  │  - GET    /api/models                                       │ │
│  │  - GET    /api/languages                                    │ │
│  │  - GET    /api/health                                       │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                            │                                       │
│     ┌──────────────────────┼──────────────────────┐               │
│     │                      │                      │               │
│     ▼                      ▼                      ▼               │
│  ┌────────────┐    ┌──────────────┐    ┌──────────────┐         │
│  │  ML/Inference│    │ Grad-CAM      │    │  Response    │        │
│  │  Module     │    │  Explainability│    │  Formatter   │        │
│  │             │    │                │    │              │        │
│  │ - Image     │    │ - Heatmap      │    │ - JSON       │        │
│  │   Preprocess│    │   Generation   │    │   Encoding   │        │
│  │ - Model     │    │ - Visualization│    │ - Status     │        │
│  │   Loading   │    │   Creation     │    │   Codes      │        │
│  │ - Inference │    │ - Overlay      │    │ - Error      │        │
│  │ - Severity  │    │   Images       │    │   Handling   │        │
│  │   Calc      │    │                │    │              │        │
│  └────────────┘    └──────────────────┘    └──────────────┘         │
└────────────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌────────────────┐ ┌──────────────┐  ┌────────────────┐
│  MODEL LAYER   │ │ DATABASE     │  │  FILE STORAGE  │
├────────────────┤ ├──────────────┤  ├────────────────┤
│ TensorFlow/    │ │ MySQL Server │  │ Local Uploads  │
│ Keras Models   │ │              │  │                │
│                │ │ Tables:      │  │ - User Images  │
│ - MobileNetV2  │ │ - Users      │  │ - Grad-CAM     │
│   92.5% Acc    │ │ - Predictions│  │ - Visualz.     │
│                │ │ - Disease    │  │                │
│ - ResNet50     │ │   Info       │  │ Max 16 MB/file │
│   94.2% Acc    │ │              │  │                │
│                │ │ Indexes on:  │  │ Cleanup:       │
│ - EfficientNetB0 │ │ - user_id    │  │ - Old files    │
│   95.8% Acc ✓  │ │ - disease    │  │ - Temp uploads │
│   (BEST)       │ │ - timestamp  │  │                │
│                │ │              │  │ (1 week TTL)   │
│ 224×224 input  │ │ Connections: │  │                │
│ 5 diseases     │ │ - Read       │  │                │
│ output         │ │ - Write      │  │                │
│                │ │ - Replication│  │                │
│ ~54 MB size    │ │              │  │                │
└────────────────┘ └──────────────┘  └────────────────┘
```

---

## 2. Data Flow Diagram

```
START
  │
  ▼
┌─────────────────────────────────┐
│  User Uploads Image             │
│  - Format: JPG/PNG/GIF          │
│  - Max Size: 16 MB              │
│  - Select Language              │
└─────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────┐
│  Server-Side Processing         │
│  1. Validate file extension     │
│  2. Check file size             │
│  3. Generate unique filename    │
│  4. Save to uploads folder      │
│  5. Load image with PIL         │
└─────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────┐
│  Image Preprocessing            │
│  1. Convert to RGB (if needed)  │
│  2. Resize to 224×224           │
│  3. Normalize [0,1]             │
│  4. Expand dims (1,224,224,3)   │
│  5. Convert to tensor           │
└─────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────┐
│  Model Inference                │
│  1. Load best_model.h5          │
│  2. Run prediction              │
│  3. Get confidence scores       │
│  4. Extract predicted class     │
│  5. Calculate max probability   │
└─────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────┐
│  Generate Grad-CAM              │
│  1. Get conv layer outputs      │
│  2. Compute gradients           │
│  3. Weight feature maps         │
│  4. Create heatmap              │
│  5. Overlay on original         │
│  6. Save visualization          │
└─────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────┐
│  Calculate Disease Severity     │
│  Formula:                       │
│  severity = confidence × 100 ×  │
│             disease_multiplier  │
│  (e.g., HLB: 0.95, Leaf Miner: 0.5)
└─────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────┐
│  Fetch from Database            │
│  1. Query disease_info table    │
│  2. Get treatment (multilingual)│
│  3. Get prevention tips         │
│  4. Get fertilizer suggestion   │
│  5. Get severity level          │
└─────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────┐
│  Save to Database               │
│  INSERT INTO predictions:       │
│  - user_id (optional)           │
│  - image_name                   │
│  - predicted_disease            │
│  - confidence_score             │
│  - disease_severity             │
│  - gradcam_path                 │
│  - timestamp                    │
└─────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────┐
│  Format Response JSON           │
│  {                              │
│    "status": "success",         │
│    "predicted_disease": "...",  │
│    "confidence": 0.958,         │
│    "severity": "87.23%",        │
│    "treatment": "...",          │
│    "prevention": "...",         │
│    "fertilizer": "...",         │
│    "gradcam_path": "...",       │
│    "all_predictions": {...}     │
│  }                              │
└─────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────┐
│  Return Response to Client      │
│  HTTP 200 OK                    │
└─────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────┐
│  Display Results in Browser     │
│  1. Show disease name           │
│  2. Display confidence %        │
│  3. Show severity bar           │
│  4. Show recommendations        │
│  5. Display Grad-CAM            │
│  6. Show prediction chart       │
└─────────────────────────────────┘
  │
  ▼
END
```

---

## 3. Database Schema Diagram

```
┌──────────────────────────────────────┐
│           USERS TABLE                │
├──────────────────────────────────────┤
│ user_id (PK, AUTO_INCREMENT)         │
│ username (UNIQUE)                    │
│ email (UNIQUE)                       │
│ password_hash                        │
│ full_name                            │
│ profile_picture                      │
│ language_preference                  │
│ created_at                           │
│ updated_at                           │
│ is_active                            │
└─────────────┬──────────────────────────────┐
              │ 1:Many                        │
              │                              │
              ▼                              │
┌──────────────────────────────────────┐    │
│       PREDICTIONS TABLE              │    │
├──────────────────────────────────────┤    │
│ prediction_id (PK)                   │◄───┘
│ user_id (FK) → Users.user_id         │
│ image_name                           │
│ image_path                           │
│ predicted_disease (FK)               │
│ confidence_score                     │
│ disease_severity                     │
│ prediction_timestamp (INDEX)         │
│ gradcam_path                         │
│ model_used                           │
│                                      │
│ Indexes:                             │
│ - idx_user_id                        │
│ - idx_disease                        │
│ - idx_timestamp                      │
└──────────────────────────────────────┘
              │
              │ Many:1
              │
              ▼
┌──────────────────────────────────────┐
│    DISEASE_INFO TABLE                │
├──────────────────────────────────────┤
│ disease_id (PK)                      │
│ disease_name (UNIQUE)                │
│ disease_name_hi                      │
│ disease_name_mr                      │
│ description                          │
│ description_hi                       │
│ description_mr                       │
│ symptoms                             │
│ symptoms_hi                          │
│ symptoms_mr                          │
│ treatment                            │
│ treatment_hi                         │
│ treatment_mr                         │
│ prevention                           │
│ prevention_hi                        │
│ prevention_mr                        │
│ fertilizer_recommendation            │
│ fertilizer_recommendation_hi         │
│ fertilizer_recommendation_mr         │
│ severity_impact                      │
│ created_at                           │
│ updated_at                           │
└──────────────────────────────────────┘
```

---

## 4. Model Training Pipeline

```
Raw Dataset
    │
    ├─ 500 images total
    ├─ 5 disease classes
    ├─ Various resolutions
    └─ Unbalanced distribution
    │
    ▼
┌─────────────────────────────────────┐
│  Data Augmentation                  │
│  - Expand dataset to ~3000 samples  │
│  - Rotation ±40°                    │
│  - Flip (H/V)                       │
│  - Zoom 0.8-1.2                     │
│  - Brightness 0.8-1.2               │
│  - Shift ±20%                       │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  Preprocessing                      │
│  - Resize all to 224×224            │
│  - Normalize [0,1]                  │
│  - Stratified split:                │
│    • 70% Train (2100)               │
│    • 15% Validation (450)           │
│    • 15% Test (450)                 │
└─────────────────────────────────────┘
    │
    ├─ Train ──────┐
    │              │
    │ Validation ─┤
    │              │
    └─ Test ──────┴──────────────────┐
                                      ▼
                    ┌─────────────────────────────────┐
                    │  Train 3 Models (Parallel)      │
                    │                                 │
                    ├─ MobileNetV2                    │
                    │  - Base: ImageNet weights       │
                    │  - Freeze base layers           │
                    │  - Custom top: 512→256→5        │
                    │  - Dropout: 0.5, 0.3            │
                    │  - Training time: 15 min        │
                    │  - Accuracy: 92.5%              │
                    │                                 │
                    ├─ ResNet50                       │
                    │  - Base: ImageNet weights       │
                    │  - Freeze base layers           │
                    │  - Custom top: 512→256→5        │
                    │  - Dropout: 0.5, 0.3            │
                    │  - Training time: 22 min        │
                    │  - Accuracy: 94.2%              │
                    │                                 │
                    └─ EfficientNetB0                 │
                       - Base: ImageNet weights       │
                       - Freeze base layers           │
                       - Custom top: 512→256→5        │
                       - Dropout: 0.5, 0.3            │
                       - Training time: 18 min        │
                       - Accuracy: 95.8% ✓            │
                    └─────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │  Evaluate on Test Set           │
                    │  - Accuracy                     │
                    │  - Precision (per class)        │
                    │  - Recall (per class)           │
                    │  - F1-Score                     │
                    │  - Confusion Matrix             │
                    │  - ROC-AUC Curves               │
                    └─────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │  Model Comparison & Selection   │
                    │                                 │
                    │  Metric        MB  ResNet EfficientNet
                    │  Accuracy     92.5  94.2   95.8 ✓
                    │  Precision    91.8  93.7   95.4 ✓
                    │  Recall       92.1  94.0   95.6 ✓
                    │  F1-Score     91.95 93.85  95.5 ✓
                    │  Model Size   27MB  98MB   54MB ✓
                    │  Inference    120ms 180ms  150ms
                    │                                 │
                    │  Decision: EfficientNetB0       │
                    │  (Best F1-Score + Small Size)   │
                    └─────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │  Save Best Model                │
                    │  - best_model.h5 (54 MB)        │
                    │  - class_mapping.json           │
                    │  - model_config.txt             │
                    │  - training_report.json         │
                    └─────────────────────────────────┘
```

---

## 5. Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    DEVELOPMENT                          │
│  Local Machine                                          │
│  - Python 3.10                                          │
│  - MySQL (local)                                        │
│  - Jupyter Notebooks                                    │
│  - VS Code / IDE                                        │
└─────────────────────────────────────────────────────────┘
                        │
                   Git Push
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                   GITHUB REPOSITORY                     │
│  - Source code                                          │
│  - Version control                                      │
│  - CI/CD triggers                                       │
└─────────────────────────────────────────────────────────┘
                        │
                   GitHub Actions
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              PRODUCTION DEPLOYMENT                      │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Container Registry (Docker Hub)                │   │
│  │  - Image:tag version management                 │   │
│  └─────────────────────────────────────────────────┘   │
│              │                                          │
│              ▼                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Load Balancer (Nginx/ALB)                      │   │
│  │  - Distribute traffic                          │   │
│  │  - SSL/TLS termination                          │   │
│  │  - Rate limiting                                │   │
│  └─────────────────────────────────────────────────┘   │
│              │                                          │
│     ┌────────┼────────┐                                │
│     ▼        ▼        ▼                                │
│  ┌────────┐┌────────┐┌────────┐                        │
│  │ Flask  ││ Flask  ││ Flask  │  (3 instances)        │
│  │ App 1  ││ App 2  ││ App 3  │                        │
│  │ :5000  ││ :5001  ││ :5002  │                        │
│  └────────┘└────────┘└────────┘                        │
│     │        │        │                                 │
│     └────────┼────────┘                                 │
│              │                                          │
│              ▼                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Shared Resources                              │   │
│  │  ┌──────────────────────────────────────────┐  │   │
│  │  │ Redis Cache (Predictions)                │  │   │
│  │  │ - Cache frequent predictions             │  │   │
│  │  │ - TTL: 24 hours                          │  │   │
│  │  └──────────────────────────────────────────┘  │   │
│  │  ┌──────────────────────────────────────────┐  │   │
│  │  │ RDS MySQL Database                       │  │   │
│  │  │ - Primary + Read Replicas                │  │   │
│  │  │ - Automated backups                      │  │   │
│  │  │ - Daily snapshots                        │  │   │
│  │  └──────────────────────────────────────────┘  │   │
│  │  ┌──────────────────────────────────────────┐  │   │
│  │  │ S3 Storage (Models, Uploads)             │  │   │
│  │  │ - best_model.h5                          │  │   │
│  │  │ - User uploaded images (temp)            │  │   │
│  │  │ - Grad-CAM visualizations                │  │   │
│  │  └──────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Monitoring & Logging                          │   │
│  │ - CloudWatch / ELK Stack                        │   │
│  │ - Prometheus metrics                            │   │
│  │ - Sentry error tracking                         │   │
│  │ - Application logs                              │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                        │
                   Domain Name
                        │
                        ▼
                  End Users
                 (Web Browser)
```

---

## 6. Component Interaction Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                      CLIENT                                 │
│  - HTML Interface                                           │
│  - Image Upload                                             │
│  - Form Submission                                          │
└──────────────────────────────────────────────────────────────┘
                            │
              ↓ REST API Request (POST /api/predict)
              ↑ JSON Response
                            │
┌──────────────────────────────────────────────────────────────┐
│                    FLASK BACKEND                            │
│                                                              │
│  1. Request Handler                                          │
│     - Validate input                                         │
│     - Extract parameters                                     │
│     - Check file size/type                                   │
│                     │                                        │
│                     ▼                                        │
│  2. Image Processing                                         │
│     - Load image (PIL)                                       │
│     - Resize (224×224)                                       │
│     - Normalize ([0,1])                                      │
│                     │                                        │
│                     ▼                                        │
│  3. Model Inference ──────┐                                 │
│     - Load model          │                                 │
│     - Run prediction      │ ──→ TensorFlow                   │
│     - Get probabilities   │    Inference                     │
│                           │    Engine                        │
│                     │     │                                 │
│                     └─────┘                                 │
│                     │                                        │
│                     ▼                                        │
│  4. Explainability Module                                    │
│     - Generate heatmap (Grad-CAM)                            │
│     - Create visualization                                   │
│     - Save to file system                                    │
│                     │                                        │
│                     ▼                                        │
│  5. Calculate Severity                                       │
│     - Apply multiplier                                       │
│     - Generate percentage                                    │
│                     │                                        │
│                     ▼                                        │
│  6. Database Query                                           │
│     - Fetch disease info                ──→ MySQL Database  │
│     - Get recommendations                   (disease_info)   │
│     - Multilingual support                                   │
│                     │                                        │
│                     ▼                                        │
│  7. Save Prediction                                          │
│     - Store metadata        ──→ MySQL Database              │
│     - User history               (predictions)               │
│     - Analytics data                                         │
│                     │                                        │
│                     ▼                                        │
│  8. Format Response                                          │
│     - Combine all results                                    │
│     - JSON serialization                                     │
│     - Error handling                                         │
│                     │                                        │
│                     ▼                                        │
│  9. Send Response                                            │
│     - HTTP 200 OK                                           │
│     - Content-Type: JSON                                     │
└──────────────────────────────────────────────────────────────┘
                            │
              ↓ JSON Response
              ↑ Render Results
                            │
┌──────────────────────────────────────────────────────────────┐
│                      CLIENT                                 │
│  - Display Disease Name                                     │
│  - Show Confidence %                                        │
│  - Display Severity Bar                                     │
│  - Show Recommendations                                     │
│  - Render Grad-CAM Heatmap                                  │
│  - Chart All Predictions                                    │
└──────────────────────────────────────────────────────────────┘
```

---

## 7. Security Architecture

```
┌───────────────────────────────────┐
│      USER (HTTPS Only)            │
└────────────┬──────────────────────┘
             │
             ▼
┌───────────────────────────────────┐
│   FIREWALL / WAF                  │
│ - IP Whitelist/Blacklist          │
│ - DDoS Protection                 │
│ - Rate Limiting                   │
└────────────┬──────────────────────┘
             │
             ▼
┌───────────────────────────────────┐
│   LOAD BALANCER (HTTPS)           │
│ - SSL/TLS Termination             │
│ - Request Validation              │
└────────────┬──────────────────────┘
             │
             ▼
┌───────────────────────────────────┐
│   API LAYER                       │
│ - Input Validation                │
│ - Parameterized Queries           │
│ - CORS Configuration              │
│ - Environment Variables           │
└────────────┬──────────────────────┘
             │
    ┌────────┼────────┐
    ▼        ▼        ▼
┌────────┐┌────────┐┌────────┐
│File    ││Model   ││Database│
│Upload  ││Inference
│Security││         │
├────────┤├────────┤├────────┤
│- Type  ││- Model ││- SQL    │
│  Validation
││  Verification
││  Injection  │
│- Size  ││         │  Prevention
│  Check ││- Input  ││- Auth     │
│- Malware││  Sanitiz-││  (User/Pass
│ Scan ││ation   ││  Hash)     │
│- Isolat││         ││- Encryption│
│- Upload││         ││            │
│ Folder ││         ││- Row-level  │
│        ││         ││  security   │
└────────┘└────────┘└────────┘

All data encrypted in transit (HTTPS) and at rest (DB encryption)
```

---

This comprehensive documentation provides a complete view of the system architecture, data flow, deployment strategy, and security considerations for the Orange Disease Detection System.
