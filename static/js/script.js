// ============================================
// Orange Disease Detection System - JavaScript
// ============================================

// Global variables
const API_BASE_URL = 'http://localhost:5000/api';
let currentLanguage = 'en';
let currentPrediction = null;
let predictionChart = null;

// Translation dictionary
const translations = {
    en: {
        home_title: 'AI-Powered Orange Disease Detection System',
        home_subtitle: 'Detect diseases in orange fruits and leaves using advanced AI technology',
        get_started: 'Get Started',
        feature_detection: 'Accurate Detection',
        feature_detection_desc: 'High accuracy disease detection using transfer learning',
        feature_analysis: 'Quick Analysis',
        feature_analysis_desc: 'Get instant predictions and severity analysis',
        feature_recommendations: 'Smart Recommendations',
        feature_recommendations_desc: 'Personalized treatment and prevention tips',
        detection_title: 'Disease Detection',
        detection_subtitle: 'Upload an image of orange leaf or fruit to detect diseases',
        upload_text: 'Upload Image',
        upload_description: 'Drag and drop or click to select',
        choose_file: 'Choose File',
        upload_icon: '📤',
        clear: 'Clear',
        predict: 'Predict Disease',
        prediction_results: 'Prediction Results',
        confidence: 'Confidence:',
        severity: 'Disease Severity:',
        treatment: 'Treatment',
        prevention: 'Prevention',
        fertilizer: 'Fertilizer Recommendation',
        explainability: 'Explainability (Grad-CAM)',
        gradcam_desc: 'The highlighted regions show which parts of the image influenced the disease detection',
        all_predictions: 'All Disease Predictions',
        predict_another: 'Predict Another Image',
        about_title: 'About This Project',
        about_objective: 'Project Objective',
        about_objective_text: 'This system uses advanced artificial intelligence and deep learning to detect diseases in orange fruits and leaves. It provides farmers with instant recommendations for treatment, prevention, and proper fertilizer usage.',
        about_technology: 'Technology Stack',
        about_diseases: 'Detected Diseases',
        about_features: 'Key Features',
        feature1: 'High Accuracy Detection',
        feature2: 'Disease Severity Analysis',
        feature3: 'Explainable AI',
        feature4: 'Multilingual Support',
        feature5: 'Prediction History',
        feature6: 'Smart Recommendations',
        contact_title: 'Contact Us',
        contact_subtitle: 'Get in Touch',
        contact_text: 'Have questions or feedback? We\'d love to hear from you!',
        email: 'Email',
        phone: 'Phone',
        location: 'Location',
        name: 'Name',
        message: 'Message',
        send_message: 'Send Message',
        footer_text: 'Using advanced AI for agricultural innovation',
        predicting: 'Predicting...'
    },
    hi: {
        home_title: 'AI-संचालित संतरे की बीमारी पहचान प्रणाली',
        home_subtitle: 'उन्नत AI तकनीक का उपयोग करके संतरे के फलों और पत्तियों में बीमारियों का पता लगाएं',
        get_started: 'शुरुआत करें',
        feature_detection: 'सटीक पहचान',
        feature_detection_desc: 'ट्रांसफर लर्निंग का उपयोग करके उच्च सटीकता की बीमारी पहचान',
        feature_analysis: 'तीव्र विश्लेषण',
        feature_analysis_desc: 'तुरंत भविष्यवाणी और गंभीरता विश्लेषण प्राप्त करें',
        feature_recommendations: 'स्मार्ट सिफारिशें',
        feature_recommendations_desc: 'व्यक्तिगत उपचार और रोकथाम सुझाव',
        detection_title: 'रोग पहचान',
        detection_subtitle: 'संतरे की पत्ती या फल की तस्वीर अपलोड करें',
        upload_text: 'तस्वीर अपलोड करें',
        upload_description: 'ड्रैग और ड्रॉप करें या क्लिक करें',
        choose_file: 'फ़ाइल चुनें',
        clear: 'साफ करें',
        predict: 'रोग की भविष्यवाणी करें',
        prediction_results: 'भविष्यवाणी के परिणाम',
        confidence: 'आत्मविश्वास:',
        severity: 'रोग की गंभीरता:',
        treatment: 'उपचार',
        prevention: 'रोकथाम',
        fertilizer: 'खाद की सिफारिश',
        explainability: 'स्पष्टता (Grad-CAM)',
        gradcam_desc: 'हाइलाइट किए गए क्षेत्र दिखाते हैं कि छवि के किस हिस्से ने रोग पहचान को प्रभावित किया',
        all_predictions: 'सभी रोग भविष्यवाणी',
        predict_another: 'दूसरी तस्वीर की भविष्यवाणी करें',
        about_title: 'इस परियोजना के बारे में',
        about_objective: 'परियोजना का उद्देश्य',
        about_objective_text: 'यह प्रणाली कृत्रिम बुद्धिमत्ता का उपयोग करके संतरे की बीमारियों का पता लगाती है।',
        about_technology: 'तकनीकी स्टैक',
        about_diseases: 'पहचानी गई बीमारियाँ',
        about_features: 'मुख्य विशेषताएं',
        feature1: 'उच्च सटीकता पहचान',
        feature2: 'रोग की गंभीरता विश्लेषण',
        feature3: 'व्याख्यायोग्य AI',
        feature4: 'बहुभाषी समर्थन',
        feature5: 'भविष्यवाणी इतिहास',
        feature6: 'स्मार्ट सिफारिशें',
        contact_title: 'हमसे संपर्क करें',
        contact_subtitle: 'संपर्क में रहें',
        contact_text: 'प्रश्न हैं? हमसे संपर्क करें!',
        email: 'ईमेल',
        phone: 'फोन',
        location: 'स्थान',
        name: 'नाम',
        message: 'संदेश',
        send_message: 'संदेश भेजें',
        footer_text: 'कृषि नवाचार के लिए AI का उपयोग करना',
        predicting: 'भविष्यवाणी जारी है...'
    },
    mr: {
        home_title: 'AI-चालित संत्र्या रोग शोध प्रणाली',
        home_subtitle: 'प्रगत AI तंत्रज्ञान वापरून संत्र्याचे फळ आणि पत्र यातील रोग शोधा',
        get_started: 'सुरु करा',
        feature_detection: 'अचूक शोध',
        feature_detection_desc: 'ट्रान्सफर लर्निंग वापरून उच्च अचूकता रोग शोध',
        feature_analysis: 'द्रुत विश्लेषण',
        feature_analysis_desc: 'त्वरित भविष्यवाणी आणि गंभीरता विश्लेषण मिळवा',
        feature_recommendations: 'स्मार्ट शिफारसी',
        feature_recommendations_desc: 'व्यक्तिगत उपचार आणि प्रतिबंध सूचना',
        detection_title: 'रोग शोध',
        detection_subtitle: 'संत्र्याचा पत्र किंवा फळ यांची प्रतिमा अपलोड करा',
        upload_text: 'प्रतिमा अपलोड करा',
        upload_description: 'ड्रॅग आणि ड्रॉप करा किंवा क्लिक करा',
        choose_file: 'फाइल निवडा',
        clear: 'साफ करा',
        predict: 'रोगाचा अंदाज लावा',
        prediction_results: 'अंदाज परिणाम',
        confidence: 'आत्मविश्वास:',
        severity: 'रोगाची गंभीरता:',
        treatment: 'उपचार',
        prevention: 'प्रतिबंध',
        fertilizer: 'खतीची शिफारस',
        explainability: 'स्पष्टता (Grad-CAM)',
        gradcam_desc: 'हाईलाइट केलेले क्षेत्र दर्शविते की प्रतिमेचा कोणता भाग रोग शोधावर प्रभाव फेलला',
        all_predictions: 'सर्व रोग अंदाज',
        predict_another: 'दुसरी प्रतिमा अंदाज लावा',
        about_title: 'या प्रकल्पाबद्दल',
        about_objective: 'प्रकल्प उद्देश्य',
        about_objective_text: 'ही प्रणाली AI वापरून संत्र्याचे रोग शोधते.',
        about_technology: 'तंत्रज्ञान स्टॅक',
        about_diseases: 'ओळखले गेलेले रोग',
        about_features: 'मुख्य वैशिष्ट्ये',
        feature1: 'उच्च अचूकता शोध',
        feature2: 'रोगाची गंभीरता विश्लेषण',
        feature3: 'स्पष्टीकरणीय AI',
        feature4: 'बहुभाषिक समर्थन',
        feature5: 'अंदाज इतिहास',
        feature6: 'स्मार्ट शिफारसी',
        contact_title: 'आमच्याशी संपर्क साधा',
        contact_subtitle: 'संपर्कात रहा',
        contact_text: 'प्रश्न आहेत का? आमच्याशी संपर्क साधा!',
        email: 'ईमेल',
        phone: 'फोन',
        location: 'स्थान',
        name: 'नाव',
        message: 'संदेश',
        send_message: 'संदेश पाठवा',
        footer_text: 'कृषी नवाचार साठी AI वापर करणे',
        predicting: 'अंदाज लावत आहे...'
    }
};

// ============================================
// Navigation Functions
// ============================================

function navigate(section) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    
    // Show selected section
    const sectionId = section + '-section';
    const sectionElement = document.getElementById(sectionId);
    if (sectionElement) {
        sectionElement.classList.add('active');
    }
    
    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    event.target.classList.add('active');
}

// ============================================
// Language Support
// ============================================

function changeLanguage() {
    const language = document.getElementById('languageSelect').value;
    currentLanguage = language;
    updateLanguage();
}

function updateLanguage() {
    const elements = document.querySelectorAll('[data-key]');
    elements.forEach(element => {
        const key = element.getAttribute('data-key');
        if (translations[currentLanguage][key]) {
            element.textContent = translations[currentLanguage][key];
        }
    });
}

// ============================================
// Image Upload Functions
// ============================================

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('uploadBox').classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('uploadBox').classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('uploadBox').classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (isValidImage(file)) {
            displayImagePreview(file);
        } else {
            alert('Please upload a valid image file');
        }
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        const file = files[0];
        if (isValidImage(file)) {
            displayImagePreview(file);
        } else {
            alert('Please upload a valid image file (JPG, PNG, GIF)');
        }
    }
}

function isValidImage(file) {
    const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
    return validTypes.includes(file.type);
}

function displayImagePreview(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.getElementById('previewImage');
        preview.src = e.target.result;
        
        document.querySelector('.upload-box').style.display = 'none';
        document.getElementById('previewArea').style.display = 'block';
        document.getElementById('predictBtn').style.display = 'block';
        document.getElementById('resultsArea').style.display = 'none';
    };
    reader.readAsDataURL(file);
}

function resetUpload() {
    document.querySelector('.upload-box').style.display = 'block';
    document.getElementById('previewArea').style.display = 'none';
    document.getElementById('predictBtn').style.display = 'none';
    document.getElementById('resultsArea').style.display = 'none';
    document.getElementById('imageInput').value = '';
}

// ============================================
// Prediction Functions
// ============================================

async function predictDisease() {
    const file = document.getElementById('imageInput').files[0];
    if (!file) {
        alert('Please select an image');
        return;
    }
    
    const formData = new FormData();
    formData.append('image', file);
    formData.append('language', currentLanguage);
    
    // Show loading spinner
    document.getElementById('loadingSpinner').style.display = 'flex';
    
    try {
        const response = await axios.post(`${API_BASE_URL}/predict`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        
        currentPrediction = response.data;
        displayPredictionResults(response.data);
        
    } catch (error) {
        console.error('Prediction error:', error);
        alert('Error making prediction: ' + error.message);
    } finally {
        document.getElementById('loadingSpinner').style.display = 'none';
    }
}

function displayPredictionResults(prediction) {
    // Display disease name
    document.getElementById('diseaseName').textContent = prediction.predicted_disease;
    
    // Display confidence
    const confidence = prediction.confidence;
    document.getElementById('confidenceValue').textContent = prediction.confidence_percentage;
    const confidenceBar = document.getElementById('confidenceBar');
    confidenceBar.style.width = (confidence * 100) + '%';
    confidenceBar.textContent = Math.round(confidence * 100) + '%';
    
    // Display severity
    const severity = parseFloat(prediction.severity);
    document.getElementById('severityValue').textContent = prediction.severity + '%';
    const severityBar = document.getElementById('severityBar');
    severityBar.style.width = severity + '%';
    severityBar.textContent = Math.round(severity) + '%';
    
    // Display recommendations
    document.getElementById('treatmentText').textContent = prediction.treatment;
    document.getElementById('preventionText').textContent = prediction.prevention;
    document.getElementById('fertilizerText').textContent = prediction.fertilizer_recommendation;
    
    // Display Grad-CAM if available
    if (prediction.gradcam_path) {
        document.getElementById('gradcamArea').style.display = 'block';
        document.getElementById('gradcamImage').src = prediction.gradcam_path;
    } else {
        document.getElementById('gradcamArea').style.display = 'none';
    }
    
    // Display all predictions chart
    displayPredictionChart(prediction.all_predictions);
    
    // Show results area
    document.getElementById('resultsArea').style.display = 'flex';
    
    // Scroll to results
    document.getElementById('resultsArea').scrollIntoView({ behavior: 'smooth' });
}

function displayPredictionChart(predictions) {
    const ctx = document.getElementById('predictionChart').getContext('2d');
    
    if (predictionChart) {
        predictionChart.destroy();
    }
    
    const labels = Object.keys(predictions);
    const data = Object.values(predictions);
    
    predictionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Prediction Confidence',
                data: data,
                backgroundColor: [
                    '#FF8C00',
                    '#FFA500',
                    '#2E7D32',
                    '#1976D2',
                    '#D32F2F'
                ],
                borderColor: '#333',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 1
                }
            }
        }
    });
}

// ============================================
// Event Listeners
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Set initial language
    updateLanguage();
    
    // Set home section as active
    navigate('home');
});

// ============================================
// API Utility Functions
// ============================================

async function getSystemStatistics() {
    try {
        const response = await axios.get(`${API_BASE_URL}/statistics`);
        return response.data;
    } catch (error) {
        console.error('Error fetching statistics:', error);
        return null;
    }
}

async function getDiseaseInfo(disease, language) {
    try {
        const response = await axios.get(`${API_BASE_URL}/disease-info/${disease}?language=${language}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching disease info:', error);
        return null;
    }
}

async function getAllDiseases(language) {
    try {
        const response = await axios.get(`${API_BASE_URL}/diseases?language=${language}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching diseases:', error);
        return null;
    }
}

async function getModelInfo() {
    try {
        const response = await axios.get(`${API_BASE_URL}/models`);
        return response.data;
    } catch (error) {
        console.error('Error fetching model info:', error);
        return null;
    }
}

// ============================================
// Utility Functions
// ============================================

function showLoading() {
    document.getElementById('loadingSpinner').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingSpinner').style.display = 'none';
}

console.log('Orange Disease Detection System - Frontend Loaded Successfully!');
