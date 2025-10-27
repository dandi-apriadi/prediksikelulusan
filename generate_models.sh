#!/bin/bash
# Quick Fix: Generate Models on Server
# Jalankan script ini di server jika file models tidak ada

echo "================================================"
echo "  Generating Machine Learning Models"
echo "================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found!"
    echo "   Please run this script from the project root directory"
    echo "   Example: cd /home/flaskapp/prediksi_app && bash generate_models.sh"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated"
    echo "   Activating virtual environment..."
    source env/bin/activate
fi

# Check if dataset exists
if [ ! -f "data/dataset.csv" ]; then
    echo "❌ Error: data/dataset.csv not found!"
    echo "   Please upload the dataset file first"
    exit 1
fi

echo "✓ Dataset found: data/dataset.csv"
echo ""

# Create models directory if not exists
mkdir -p models
echo "✓ Models directory ready"
echo ""

# Check if training script exists
if [ ! -f "src/training.py" ]; then
    echo "❌ Error: src/training.py not found!"
    exit 1
fi

echo "✓ Training script found"
echo ""

# Run training
echo "🚀 Starting model training..."
echo "   This may take several minutes depending on dataset size"
echo ""
python src/training.py

# Check if models were created
if [ $? -eq 0 ]; then
    echo ""
    echo "================================================"
    echo "✅ SUCCESS! Models generated successfully"
    echo "================================================"
    echo ""
    echo "Generated models:"
    ls -lh models/
    echo ""
    echo "You can now run the application:"
    echo "  python app.py"
    echo ""
    echo "Or start with Gunicorn:"
    echo "  gunicorn --workers 4 --bind unix:prediksi.sock -m 007 app:app"
else
    echo ""
    echo "================================================"
    echo "❌ ERROR: Model training failed!"
    echo "================================================"
    echo ""
    echo "Please check the error messages above"
    echo "Common issues:"
    echo "  - Missing dependencies: pip install -r requirements-linux.txt"
    echo "  - Invalid dataset format"
    echo "  - Insufficient memory"
    exit 1
fi
