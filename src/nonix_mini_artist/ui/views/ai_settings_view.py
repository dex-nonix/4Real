"""
AI Settings view for managing Google AI providers and presets
"""
from nicegui import ui
from ..components.generic_table import GenericTable
from ..components.generic_form import GenericForm
from ..components.search_bar import EntitySearchBar
from ...ai.service import AIService
from ...ai.models import AIPreset, AIProviderConfig

class AISettingsView:
    """AI Settings view for managing Google AI integration"""
    
    def __init__(self, ai_service: AIService):
        """Initialize AI settings view"""
        self.ai_service = ai_service
        self.providers = []
        self.presets = []
        self._build_view()
        self._load_data()
    
    def _build_view(self):
        """Build the AI settings view"""
        with ui.column().classes('w-full'):
            # Header
            ui.label('🤖 AI Settings').classes('text-3xl font-bold mb-6')
            ui.label('Manage Google AI providers and analysis presets').classes('text-lg text-gray-600 mb-6')
            
            # Tabs for different AI settings
            with ui.tabs().classes('w-full mb-6') as tabs:
                ui.tab('Providers', icon='🔧')
                ui.tab('Presets', icon='⚙️')
                ui.tab('Analysis', icon='🔍')
            
            # Providers Tab
            with ui.tab_panels(tabs, value='Providers').classes('w-full'):
                # Providers Panel
                with ui.tab_panel('Providers'):
                    self._build_providers_panel()
                
                # Presets Panel
                with ui.tab_panel('Presets'):
                    self._build_presets_panel()
                
                # Analysis Panel
                with ui.tab_panel('Analysis'):
                    self._build_analysis_panel()
    
    def _build_providers_panel(self):
        """Build the providers management panel"""
        with ui.column().classes('w-full'):
            # Add new provider button
            ui.button('➕ Add New Provider', on_click=self._show_add_provider_form).classes('mb-6 bg-green-500 text-white hover:bg-green-600')
            
            # Providers table
            self.providers_table = GenericTable(
                data=self.providers,
                columns=['name', 'enabled', 'config'],
                actions=['test', 'edit', 'delete'],
                crud_operations=None  # Custom handling for providers
            )
            
            # Add provider form (hidden by default)
            self.add_provider_form = self._create_provider_form()
            self.add_provider_form.visible = False
    
    def _build_presets_panel(self):
        """Build the presets management panel"""
        with ui.column().classes('w-full'):
            # Add new preset button
            ui.button('➕ Add New Preset', on_click=self._show_add_preset_form).classes('mb-6 bg-blue-500 text-white hover:bg-blue-600')
            
            # Presets table
            self.presets_table = GenericTable(
                data=self.presets,
                columns=['name', 'provider', 'model', 'enabled'],
                actions=['view', 'edit', 'delete'],
                crud_operations=None  # Custom handling for presets
            )
            
            # Add preset form (hidden by default)
            self.add_preset_form = self._create_preset_form()
            self.add_preset_form.visible = False
    
    def _build_analysis_panel(self):
        """Build the analysis testing panel"""
        with ui.column().classes('w-full'):
            ui.label('Test AI Analysis').classes('text-xl font-bold mb-4')
            
            # Analysis test form
            with ui.card().classes('w-full max-w-2xl p-6'):
                # Preset selection
                ui.label('Select Analysis Preset:').classes('font-bold mb-2')
                self.preset_select = ui.select(
                    options=[], 
                    value='',
                    label='Preset'
                ).classes('w-full mb-4')
                
                # Content input
                ui.label('Content to Analyze:').classes('font-bold mb-2')
                self.content_input = ui.textarea(
                    label='Content',
                    value='',
                    placeholder='Enter lyrics, description, or other content to analyze...'
                ).classes('w-full mb-4')
                
                # Context input
                ui.label('Additional Context (Optional):').classes('font-bold mb-2')
                self.context_input = ui.textarea(
                    label='Context',
                    value='',
                    placeholder='Genre, artist, mood, etc.'
                ).classes('w-full mb-4')
                
                # Analyze button
                ui.button('🔍 Analyze with AI', on_click=self._run_analysis).classes('w-full bg-purple-500 text-white hover:bg-purple-600')
                
                # Results area
                ui.separator().classes('my-4')
                ui.label('Analysis Results:').classes('font-bold mb-2')
                self.results_area = ui.markdown('').classes('w-full p-4 bg-gray-100 rounded')
    
    def _create_provider_form(self):
        """Create the add provider form"""
        with ui.card().classes('w-full max-w-2xl mx-auto p-6') as form:
            ui.label('Add New AI Provider').classes('text-2xl font-bold mb-6')
            
            # Provider type selection
            ui.label('Provider Type:').classes('font-bold mb-2')
            provider_type = ui.select(
                options=['gemini', 'vertex'],
                value='gemini',
                label='Provider'
            ).classes('w-full mb-4')
            
            # API Key input
            ui.label('API Key:').classes('font-bold mb-2')
            api_key = ui.input(
                label='API Key',
                value='',
                password=True
            ).classes('w-full mb-4')
            
            # Project ID (for Vertex AI)
            ui.label('Project ID (Vertex AI only):').classes('font-bold mb-2')
            project_id = ui.input(
                label='Project ID',
                value=''
            ).classes('w-full mb-4')
            
            # Location (for Vertex AI)
            ui.label('Location (Vertex AI only):').classes('font-bold mb-2')
            location = ui.input(
                label='Location',
                value='us-central1'
            ).classes('w-full mb-4')
            
            # Submit button
            ui.button('Add Provider', on_click=lambda: self._create_provider(
                provider_type.value,
                api_key.value,
                project_id.value,
                location.value
            )).classes('w-full mt-6 bg-blue-500 text-white hover:bg-blue-600')
            
            return form
    
    def _create_preset_form(self):
        """Create the add preset form"""
        with ui.card().classes('w-full max-w-2xl mx-auto p-6') as form:
            ui.label('Add New AI Preset').classes('text-2xl font-bold mb-6')
            
            # Preset name
            ui.label('Preset Name:').classes('font-bold mb-2')
            name = ui.input(
                label='Name',
                value=''
            ).classes('w-full mb-4')
            
            # Provider selection
            ui.label('AI Provider:').classes('font-bold mb-2')
            provider = ui.select(
                options=['gemini', 'vertex'],
                value='gemini',
                label='Provider'
            ).classes('w-full mb-4')
            
            # Model selection
            ui.label('Model:').classes('font-bold mb-2')
            model = ui.input(
                label='Model',
                value='gemini-1.5-pro'
            ).classes('w-full mb-4')
            
            # System prompt
            ui.label('System Prompt:').classes('font-bold mb-2')
            system_prompt = ui.textarea(
                label='System Prompt',
                value=''
            ).classes('w-full mb-4')
            
            # Temperature
            ui.label('Temperature (Creativity):').classes('font-bold mb-2')
            temperature = ui.slider(
                min=0.0, max=2.0, step=0.1, value=0.7
            ).classes('w-full mb-4')
            
            # Max tokens
            ui.label('Max Tokens:').classes('font-bold mb-2')
            max_tokens = ui.number(
                label='Max Tokens',
                value=1000
            ).classes('w-full mb-4')
            
            # Submit button
            ui.button('Add Preset', on_click=lambda: self._create_preset(
                name.value,
                provider.value,
                model.value,
                system_prompt.value,
                temperature.value,
                max_tokens.value
            )).classes('w-full mt-6 bg-blue-500 text-white hover:bg-blue-600')
            
            return form
    
    async def _load_data(self):
        """Load AI service data"""
        try:
            # Get providers and presets
            self.providers = self.ai_service.get_providers()
            self.presets = self.ai_service.get_presets()
            
            # Update tables
            if hasattr(self, 'providers_table'):
                self.providers_table.update_data(self.providers)
            
            if hasattr(self, 'presets_table'):
                self.presets_table.update_data(self.presets)
            
            # Update preset select options
            if hasattr(self, 'preset_select'):
                preset_options = [preset.name for preset in self.presets]
                self.preset_select.options = preset_options
            
        except Exception as e:
            ui.notify(f'Error loading AI data: {str(e)}', type='negative')
    
    async def _create_provider(self, provider_type: str, api_key: str, project_id: str, location: str):
        """Create a new AI provider"""
        try:
            config = {
                'name': provider_type,
                'api_key': api_key,
                'enabled': True
            }
            
            if provider_type == 'vertex':
                config['project_id'] = project_id
                config['location'] = location
            
            self.ai_service.add_provider(config)
            await self._load_data()
            self.add_provider_form.visible = False
            ui.notify('Provider created successfully!', type='positive')
            
        except Exception as e:
            ui.notify(f'Error creating provider: {str(e)}', type='negative')
    
    async def _create_preset(self, name: str, provider: str, model: str, system_prompt: str, temperature: float, max_tokens: int):
        """Create a new AI preset"""
        try:
            preset = AIPreset(
                name=name,
                provider=provider,
                model=model,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            self.ai_service.add_preset(preset)
            await self._load_data()
            self.add_preset_form.visible = False
            ui.notify('Preset created successfully!', type='positive')
            
        except Exception as e:
            ui.notify(f'Error creating preset: {str(e)}', type='negative')
    
    def _show_add_provider_form(self):
        """Show the add provider form"""
        self.add_provider_form.visible = True
    
    def _show_add_preset_form(self):
        """Show the add preset form"""
        self.add_preset_form.visible = True
    
    async def _run_analysis(self):
        """Run AI analysis on the provided content"""
        try:
            if not self.preset_select.value:
                ui.notify('Please select a preset', type='warning')
                return
            
            if not self.content_input.value.strip():
                ui.notify('Please enter content to analyze', type='warning')
                return
            
            # Show loading
            self.results_area.content = '🔄 Analyzing with AI...'
            
            # Create analysis request
            from ...ai.models import AIAnalysisRequest
            request = AIAnalysisRequest(
                preset_name=self.preset_select.value,
                content=self.content_input.value,
                context={'context': self.context_input.value} if self.context_input.value.strip() else None
            )
            
            # Run analysis
            response = await self.ai_service.analyze(request)
            
            if response.success:
                # Display results
                self.results_area.content = f"""
## AI Analysis Results

**Provider:** {response.provider}
**Model:** {response.model}
**Content:** {response.content}

**Usage:** {response.usage or 'N/A'}
                """
                ui.notify('Analysis completed successfully!', type='positive')
            else:
                # Display error
                self.results_area.content = f"""
## Analysis Failed

**Error:** {response.error}
                """
                ui.notify(f'Analysis failed: {response.error}', type='negative')
                
        except Exception as e:
            self.results_area.content = f"""
## Analysis Error

**Error:** {str(e)}
            """
            ui.notify(f'Error running analysis: {str(e)}', type='negative')
    
    async def refresh_data(self):
        """Refresh AI settings data"""
        await self._load_data()
