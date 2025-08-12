# 🤖 Google AI Integration Guide

## Overview

The Nonix Mini Artist Manager now includes comprehensive Google AI integration for intelligent music analysis and management. This feature allows you to analyze lyrics, classify styles, and generate content using Google's advanced AI models.

## 🚀 Features

### AI Providers
- **Google Gemini**: Text generation and analysis using Gemini models
- **Google Vertex AI**: Enterprise-grade AI services (requires Google Cloud)

### AI Analysis Presets
- **Lyrics Analyzer**: Deep analysis of song lyrics for themes and cultural context
- **Style Classifier**: Automatic classification of music genres and styles
- **Content Generator**: AI-powered content creation for descriptions and bios

### Runtime Management
- **Hot-swap providers** without restarting the application
- **Dynamic configuration** updates
- **Real-time testing** of AI connections
- **Usage monitoring** and cost tracking

## 🛠️ Setup

### 1. Install Dependencies

```bash
# Install the updated package
pip install -e .

# Or install manually
pip install google-generativeai google-cloud-aiplatform python-dotenv
```

### 2. Configure Google AI

#### Option A: Environment Variables
```bash
# For Gemini
export GOOGLE_API_KEY="your_api_key_here"

# For Vertex AI
export GOOGLE_CLOUD_PROJECT="your_project_id"
export GOOGLE_CLOUD_LOCATION="us-central1"
```

#### Option B: Configuration File
Copy `config/ai_config.example.json` to `config/ai_config.json` and update with your credentials:

```json
{
  "providers": [
    {
      "name": "gemini",
      "api_key": "your_actual_api_key",
      "enabled": true
    }
  ]
}
```

### 3. Get Google AI Credentials

#### Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your configuration

#### Vertex AI (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Vertex AI API
3. Create a service account with appropriate permissions
4. Download the JSON key file

## 🎯 Usage

### AI Settings Management

1. **Navigate to AI Settings**: Click the "🤖 AI Settings" button in the sidebar
2. **Manage Providers**: Add, edit, and test Google AI providers
3. **Configure Presets**: Create custom analysis presets for different use cases
4. **Test Analysis**: Use the built-in testing interface to verify AI functionality

### Track Analysis

1. **Go to Tracks View**: Navigate to the Tracks section
2. **Click AI Analysis**: Use the "🤖 AI Analysis" button
3. **Select Track**: Choose a track to analyze
4. **Choose Preset**: Select an analysis type (lyrics, style, content)
5. **Run Analysis**: Click "Analyze with AI" to get results

### Batch Processing

The AI service supports analyzing multiple tracks and albums:
- Select multiple items for analysis
- Choose appropriate presets for each analysis type
- Export results to database or files

## 🔧 Configuration

### Provider Settings

#### Gemini Provider
```json
{
  "name": "gemini",
  "api_key": "your_api_key",
  "enabled": true
}
```

#### Vertex AI Provider
```json
{
  "name": "vertex",
  "project_id": "your_project_id",
  "location": "us-central1",
  "enabled": true
}
```

### Preset Configuration

```json
{
  "name": "custom_analyzer",
  "provider": "gemini",
  "model": "gemini-1.5-pro",
  "system_prompt": "Your custom system prompt here",
  "temperature": 0.7,
  "max_tokens": 1000,
  "enabled": true
}
```

### Advanced Settings

- **Temperature**: Controls AI creativity (0.0 = focused, 2.0 = creative)
- **Max Tokens**: Limits response length
- **System Prompts**: Define AI behavior and expertise

## 📊 Monitoring

### Usage Statistics
- Track API calls and costs
- Monitor response times
- View success/failure rates

### Cost Management
- Set usage limits
- Monitor API quotas
- Track spending by provider

## 🚨 Troubleshooting

### Common Issues

#### "Provider not initialized"
- Check API key configuration
- Verify provider is enabled
- Test connection in AI Settings

#### "Analysis failed"
- Check content length and format
- Verify preset configuration
- Review API quotas and limits

#### "Model not available"
- Check model name spelling
- Verify provider supports the model
- Update to supported model versions

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔒 Security

### API Key Management
- Store keys in environment variables
- Use configuration files with restricted permissions
- Rotate keys regularly
- Monitor for unauthorized usage

### Data Privacy
- AI analysis runs locally
- No data sent to Google unless explicitly configured
- Review Google's data usage policies

## 📈 Performance

### Optimization Tips
- Use appropriate model sizes for tasks
- Batch similar analysis requests
- Cache common analysis results
- Monitor API response times

### Scaling
- Add multiple providers for redundancy
- Use different models for different tasks
- Implement rate limiting for API calls

## 🔮 Future Features

### Planned Enhancements
- **Multi-language support** for international music
- **Audio analysis** using Google's audio models
- **Real-time collaboration** with AI insights
- **Advanced analytics** and reporting
- **Integration** with other AI providers

### Custom Models
- Fine-tune models for specific music genres
- Create domain-specific analysis presets
- Build custom AI workflows

## 📚 Examples

### Basic Analysis
```python
from nonix_mini_artist.ai.service import AIService
from nonix_mini_artist.ai.models import AIAnalysisRequest

# Initialize AI service
ai_service = AIService()

# Create analysis request
request = AIAnalysisRequest(
    preset_name="lyrics_analyzer",
    content="Your lyrics here...",
    context={"genre": "dancehall", "artist": "TRC"}
)

# Run analysis
response = await ai_service.analyze(request)
print(response.content)
```

### Custom Preset
```python
from nonix_mini_artist.ai.models import AIPreset

# Create custom preset
preset = AIPreset(
    name="reggae_analyzer",
    provider="gemini",
    model="gemini-1.5-pro",
    system_prompt="You are a reggae music expert...",
    temperature=0.5,
    max_tokens=800
)

# Add to service
ai_service.add_preset(preset)
```

## 🆘 Support

### Getting Help
- Check the troubleshooting section above
- Review Google AI documentation
- Check application logs for errors
- Verify configuration settings

### Resources
- [Google AI Studio](https://makersuite.google.com/)
- [Google Cloud Vertex AI](https://cloud.google.com/vertex-ai)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)

---

**The Google AI integration transforms your music manager into an intelligent assistant that can understand, analyze, and enhance your music collection! 🎵✨**
