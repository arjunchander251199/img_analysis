# AI Image Analyzer

A modern Flask-based single-page application that uses Google's Gemini 1.5 Pro AI to extract and analyze content from images, including handwritten text.

## Features

- 📤 **Image Upload**: Support for PNG, JPG, GIF, BMP, and WebP formats
- 🤖 **AI-Powered Analysis**: Uses Gemini 3.5 Pro for intelligent content extraction
- ✍️ **Handwriting Recognition**: Extracts both printed and handwritten text
- ✏️ **Editable Output**: Modify extracted content with inline editing
- 📋 **Copy & Download**: Export results to clipboard or text file
- 📱 **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- ⚡ **Real-time Processing**: Live progress indicators during analysis
- 🎨 **Modern UI**: Built with Tailwind CSS for a beautiful interface

## Installation

### Prerequisites

- Python 3.8+
- Node.js 14+ (for Tailwind CSS)

### Setup

1. **Install Python dependencies:**

```bash
pip install -r requirements.txt
```

2. **Install Node.js dependencies:**

```bash
npm install
```

3. **Build Tailwind CSS:**

```bash
npm run build:css
```

## Usage

### Run the application:

```bash
python run.py
```

The application will be available at `http://localhost:5000`

### Development Mode

To watch for CSS changes during development:

```bash
npm run watch:css
```

## Project Structure

```
image_analyzer/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── main/                    # Main blueprint
│   │   ├── __init__.py
│   │   └── routes.py            # Main routes
│   ├── api/                     # API blueprint
│   │   ├── __init__.py
│   │   └── routes.py            # API endpoints
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   └── gemini_service.py    # Gemini AI integration
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py
│   │   └── file_handler.py      # File operations
│   ├── static/
│   │   ├── css/
│   │   │   ├── input.css        # Tailwind input
│   │   │   └── output.css       # Compiled CSS
│   │   ├── js/
│   │   │   └── app.js           # Frontend logic
│   │   └── uploads/             # Temporary file storage
│   └── templates/
│       └── index.html           # SPA template
├── config.py                    # Configuration
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── package.json                 # Node.js dependencies
└── tailwind.config.js           # Tailwind configuration
```

## API Endpoints

### POST /api/upload

Upload an image for processing

- **Body**: multipart/form-data with 'file' field
- **Response**: `{ success: true, filename: string, file_url: string }`

### POST /api/analyze

Analyze uploaded image with AI

- **Body**: `{ filename: string }`
- **Response**: `{ success: true, result: { type: string, content: ... } }`

### DELETE /api/delete/:filename

Delete uploaded file

- **Response**: `{ success: true, message: string }`

## Configuration

Edit `config.py` to customize:

- Upload folder location
- Maximum file size
- Allowed file extensions
- Gemini API settings

## Technologies Used

- **Backend**: Flask, Python
- **AI**: Google Gemini 3.5 Pro
- **Frontend**: Vanilla JavaScript, Tailwind CSS
- **Image Processing**: Pillow
- **Architecture**: Blueprint pattern, modular design

## Running in Production

For production deployment, use Gunicorn with the provided configuration:

```bash
gunicorn -c gunicorn_config.py run:app
```

Or simply:

```bash
gunicorn run:app --bind 0.0.0.0:5000 --timeout 120 --workers 4
```

## Troubleshooting

### 502 Error / Empty JSON Response

If you encounter a 502 error or "Failed to execute 'json' on 'Response'" error:

1. **Check API Key**: Ensure your Gemini API key is valid and has quota remaining
2. **Timeout Issues**: Large or complex images may timeout. The app now has:
   - 60-second timeout on Gemini API requests
   - 120-second timeout on Gunicorn workers
   - Automatic retry with exponential backoff
3. **Image Size**: Try resizing images to under 1536px for faster processing
4. **Check Logs**: Look at the terminal/console for detailed error messages

### Common Error Codes

- **429**: API quota exceeded - wait and try again
- **504**: Request timeout - image is too complex or API is slow
- **500**: General server error - check logs for details

### Debug Mode

The app runs in debug mode by default with `python run.py`. For production, disable debug mode or use Gunicorn.

## Security Notes

- API key is hardcoded for development. Use environment variables in production.
- Uploaded files are stored temporarily and can be deleted after analysis.
- Maximum file size is limited to 16MB by default.

## License

MIT License
