import gradio as gr
from fpdf import FPDF
from IPython.display import display, HTML, Markdown
import datetime
import requests
import os
from crewai import Agent, Task, Process, Crew, LLM
from dotenv import load_dotenv
#from crewai_tools import SerperDevTool

# Load environment variables
load_dotenv()

# Configure your LLM - Using Groq
api_key = os.getenv("GROQ_API_KEY")
llm_groq = LLM(model="groq/llama3-8b-8192", api_key=api_key, temperature=0.4)
llm_groq_1 = LLM(model="groq/deepseek-r1-distill-llama-70b", api_key=api_key, temperature=0.4)
llm_groq_2 = LLM(model="groq/llama3-8b-8192", api_key=api_key, temperature=0.3)
llm_groq_3 = LLM(model="groq/gemma2-9b-it", api_key=api_key, temperature=0.6)
def create_agents():
    return [
        Agent(
            role="Agro-Climate Specialist",
            goal="Analyze soil and climate conditions with adaptation strategies",
            backstory="Expert in soil science and climate-smart agriculture",
            llm=llm_groq,
            verbose=True
        ),
        Agent(
            role="Crop Health Manager",
            goal="Recommend fertilizers and pest/disease solutions",
            backstory="Plant pathologist with organic farming expertise",
            llm=llm_groq_1,
            verbose=True
        ),
        Agent(
            role="Agricultural Economist",
            goal="Evaluate costs, viability and regional benefits",
            backstory="Agricultural financial analyst with market knowledge",
            llm=llm_groq_2,
            verbose=True
        ),
        Agent(
            role="Farm Advisory Writer",
            goal="Compile actionable farmer recommendations",
            backstory="Agricultural extension officer with technical writing skills",
            llm=llm_groq_3,
            verbose=True
        )
    ]

def create_tasks(agents, crop, region, soil_data, farm_size):
    # First create all tasks without context
    weather_info = get_weather_data(region)
    tasks = [
        Task(
            description=f"""Analyze for {crop} in {region}:
            1. Soil requirements based on: {soil_data}
            2. Current weather patterns: {weather_info}
            3. Climate adaptation strategies""",
            expected_output="Detailed soil-climate analysis with weather considerations",
            agent=agents[0]
        ),
        Task(
            description=f"""Recommend for {crop}:
            1. Fertilizer requirements
            2. Common pests and organic controls
            3. Potential diseases""",
            expected_output="Crop health management plan",
            agent=agents[1]
        ),
        Task(
            description=f"""Analyze for {crop} in {region}:
            1. Cost-benefit of recommendations
            2. Market potential
            3. Government support programs""",
            expected_output="Economic viability report",
            agent=agents[2]
        )
    ]
    
    # Now create the report task with context
    report_task = Task(
        description="Create farmer-friendly guide by compiling:",
        expected_output="Final advisory document in markdown format",
        agent=agents[3],
        context=tasks  # Pass all previous tasks as context
    )
    
    return tasks + [report_task]  # Return all tasks including the report task
    
def run_analysis(crop, region, soil_data, farm_size):
    """Run the sustainable farming advisory analysis"""
    agents = create_agents()
    tasks = create_tasks(agents, crop, region, soil_data, farm_size)
    
    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential, # Sequential execution of tasks
        verbose=True #Shows detailed execution logs
    )
    
    result = crew.kickoff()
    #markdown_result = result.to_markdown()  # Convert the result to markdown format
    #final_result_text = str(markdown_result)  # Store the result
    final_result_text = str(result)
    return final_result_text

def get_weather_data(region):
    """Fetch current weather data for the region"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Weather API key not configured"
    
    try:
        # First try to get coordinates for the region
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={region}&limit=1&appid={api_key}"
        geo_response = requests.get(geo_url)
        geo_data = geo_response.json()
        
        if not geo_data:
            return "Location not found"
            
        lat, lon = geo_data[0]['lat'], geo_data[0]['lon']
        
        # Get weather data
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()
        
        # Format the weather information
        return (
            f"Current Temperature: {weather_data['main']['temp']}°C\n"
            f"Conditions: {weather_data['weather'][0]['description']}\n"
            f"Humidity: {weather_data['main']['humidity']}%\n"
            f"Wind Speed: {weather_data['wind']['speed']} m/s\n"
            f"Pressure: {weather_data['main']['pressure']} hPa"
        )
    except Exception as e:
        return f"Could not fetch weather data: {str(e)}"

def generate_pdf(final_result_text):
    """Generate PDF from the analysis result"""
    # Create the PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, final_result_text)

    # Save it
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"advisory_report_{date}.pdf"
    filepath = f"./{filename}"
    pdf.output(filepath)

    return filepath

def clear_input():
    return "", "", "", ""  # Clear the inputs

# Create the Gradio Interface
with gr.Blocks() as app:
    gr.Markdown("# 🌾 Sustainable Farming Advisory System")
    
    with gr.Row():
        with gr.Column():
            crop_input = gr.Textbox(label="Crop Type (e.g., Wheat, Maize)", value="Maize")
            region_input = gr.Textbox(label="Region (e.g., Axum, Rende)", value="Axum")
            soil_input = gr.Textbox(label="Soil Data (e.g., pH: 6.2, Nitrogen: medium)", value="pH: 6.2, Nitrogen: medium")
            farm_size_input = gr.Textbox(label="Farm Size (e.g., 400 acres)", value="400 acres")
            
            # Add weather preview button
            weather_button = gr.Button("Preview Weather 🌤️")
            weather_output = gr.Textbox(label="Current Weather", interactive=False)

        with gr.Column():
            output_text = gr.Textbox(label="Analysis Results", lines=15)
    
    with gr.Row():
        # Add weather button functionality
        weather_button.click(get_weather_data, inputs=region_input, outputs=weather_output)
    
        # ... rest of your existing buttons and functionality ...
        analyze_button = gr.Button("Run Analysis ✅")
        clear_button = gr.Button("Clear")
        download_button = gr.Button("📥 Download Report as PDF")
        download_file = gr.File(label="Click to download your PDF report 📄")
        

    # Button click actions
    analyze_button.click(run_analysis, inputs=[crop_input, region_input, soil_input, farm_size_input], outputs=output_text)
    clear_button.click(clear_input, outputs=[crop_input, region_input, soil_input, farm_size_input])
    download_button.click(generate_pdf, inputs=[output_text], outputs=download_file)  # Pass result to generate PDF

# Launch the app
if __name__ == "__main__":
    app.launch()
