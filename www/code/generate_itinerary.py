
import json

def generate_html(data):
    # Helper function to generate itinerary items
    def generate_itinerary_items(items):
        html = ""
        for item in items:
            html += f"""
                        <div class="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
                            <div class="text-indigo-500"><i data-feather="{item['icon']}" class="icon-style"></i></div>
                            <p class="text-gray-700">{item['text']}</p>
                        </div>
            """
        return html

    # Helper function to generate itinerary days
    def generate_itinerary_days():
        html = ""
        for day in data['itinerary']:
            html += f"""
                <div id="day-{day['day']}-content" class="day-content {'hidden' if day['day'] > 1 else ''}">
                    <h3 class="text-xl font-bold text-center mb-4">{day['title']}</h3>
                    <div class="space-y-4">
                        {generate_itinerary_items(day['items'])}
                    </div>
                    <div class="text-right mt-4 font-bold text-lg text-indigo-600">Approx. Daily Cost: {day['dailyCost']}</div>
                </div>
            """
        return html

    # Helper function to generate itinerary tabs
    def generate_itinerary_tabs():
        html = ""
        for day in data['itinerary']:
            html += f"""
                    <button class="tab-button font-semibold py-2 px-4 rounded-full text-sm sm:text-base {'active' if day['day'] == 1 else ''}" data-day="{day['day']}">Day {day['day']}</button>
            """
        return html
        
    # Helper function to generate travel options
    def generate_travel_options():
        html = ""
        for option in data['planning']['travelOptions']:
            link_tag = f'href="{option["link"]}" target="_blank"' if 'link' in option else ''
            html += f"""
                        <a {link_tag} class="travel-option-card block">
                            <div class="flex justify-center mb-2"><i data-feather="{option['icon']}" class="icon-style text-blue-500"></i></div>
                            <h4 class="font-bold flex items-center justify-center">{option['type']} {'<i data-feather="external-link" class="w-4 h-4 ml-2"></i>' if 'link' in option else ''}</h4>
                            <p class="text-sm text-gray-600">{option['details']}</p>
                        </a>
            """
        return html

    # Helper function to generate cost summary
    def generate_cost_summary():
        html = ""
        for item in data['costs']['summary']:
            html += f"""
                    <div class="p-4 bg-gray-50 rounded-lg">
                        <h4 class="font-semibold text-gray-500 text-sm">{item['item']}</h4>
                        <p class="font-bold text-2xl text-indigo-600">{item['amount']}</p>
                    </div>
            """
        return html

    # Helper function to generate other places
    def generate_other_places():
        html = ""
        for place in data['otherPlaces']:
            html += f"""
                    <a href="{place['link']}" target="_blank" class="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                        <div class="text-purple-500 pt-1"><i data-feather="{place['icon']}" class="icon-style"></i></div>
                        <div>
                            <h4 class="font-bold text-indigo-600 hover:underline flex items-center">{place['name']} <i data-feather="external-link" class="w-4 h-4 ml-2"></i></h4>
                            <p class="text-sm text-gray-600">{place['description']}</p>
                        </div>
                    </a>
            """
        return html

    # Main HTML structure
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['title']}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/feather-icons"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>
    <style>
        body {{
            font-family: 'Poppins', sans-serif;
            background-color: #f0f2f5;
            color: #333;
        }}
        .header-bg {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .tab-button {{
            transition: all 0.3s ease;
        }}
        .tab-button.active {{
            background-color: #667eea;
            color: white;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .card {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.07);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }}
        .icon-style {{
            width: 24px;
            height: 24px;
            stroke-width: 2;
        }}
        .cost-summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }}
        .travel-option-card {{
             background-color: #fafafa;
             border-radius: 10px;
             padding: 1rem;
             transition: all 0.3s ease;
             border: 1px solid #e5e7eb;
        }}
        .travel-option-card:hover {{
            border-color: #667eea;
            background-color: #fff;
        }}
    </style>
</head>
<body class="antialiased">

    <header class="header-bg text-white text-center py-12 sm:py-20">
        <div class="container mx-auto px-4">
            <h1 class="text-4xl sm:text-5xl font-bold tracking-tight">{data['title']}</h1>
            <p class="mt-4 text-lg sm:text-xl opacity-90">{data['subtitle']}</p>
        </div>
    </header>

    <main class="container mx-auto px-4 py-8 sm:py-12">
        
        <!-- Itinerary Section -->
        <section id="itinerary" class="mb-12">
            <div class="card p-6 sm:p-8">
                <h2 class="text-2xl sm:text-3xl font-bold text-center mb-6">Daily Itinerary</h2>
                <div id="tabs-container" class="flex justify-center space-x-2 sm:space-x-4 bg-gray-100 p-2 rounded-full mb-6">
                    {generate_itinerary_tabs()}
                </div>
                <div id="tab-content">
                    {generate_itinerary_days()}
                </div>
            </div>
        </section>

        <!-- Trip Planning Section -->
        <section id="planning" class="mb-12">
            <div class="card p-6 sm:p-8">
                <h2 class="text-2xl sm:text-3xl font-bold text-center mb-4">Trip Planning</h2>
                <p class="text-center text-sm text-indigo-600 mb-8">Click the options with the <i data-feather="external-link" class="inline-block w-4 h-4"></i> icon for more details.</p>
                
                <!-- Travel Options -->
                <div class="mb-10">
                    <h3 class="text-xl font-bold mb-4 text-gray-700">Travel Options</h3>
                    <div class="grid md:grid-cols-3 gap-6 text-center">
                        {generate_travel_options()}
                    </div>
                </div>

                <!-- Pre-trip Checklist -->
                <div>
                    <h3 class="text-xl font-bold mb-4 text-gray-700">Pre-Trip Checklist</h3>
                    <div class="grid md:grid-cols-2 gap-8">
                        <div class="flex items-start space-x-4">
                            <div class="bg-blue-100 text-blue-600 p-3 rounded-full"><i data-feather="briefcase" class="icon-style"></i></div>
                            <div>
                                <h3 class="font-bold text-lg">Things to Pack</h3>
                                <ul class="mt-2 list-disc list-inside text-gray-600">
                                    {''.join(f"<li>{item}</li>" for item in data['planning']['checklist']['packing'])}
                                </ul>
                            </div>
                        </div>
                        <div class="flex items-start space-x-4">
                            <div class="bg-green-100 text-green-600 p-3 rounded-full"><i data-feather="wifi" class="icon-style"></i></div>
                            <div>
                                <h3 class="font-bold text-lg">Connectivity</h3>
                                <ul class="mt-2 list-disc list-inside text-gray-600">
                                    {''.join(f"<li>{item}</li>" for item in data['planning']['checklist']['connectivity'])}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Cost Summary -->
        <section id="costs">
            <div class="card p-6 sm:p-8">
                <h2 class="text-2xl sm:text-3xl font-bold text-center mb-8">Trip Cost Summary</h2>
                <div class="cost-summary-grid text-center">
                    {generate_cost_summary()}
                </div>
                <div class="mt-8 text-center bg-indigo-600 text-white p-4 rounded-lg">
                    <h4 class="font-semibold text-lg">Total Estimated Cost Per Person</h4>
                    <p class="font-bold text-3xl tracking-tight">{data['costs']['total']}</p>
                </div>
            </div>
        </section>

        <!-- Other Places to Explore -->
        <section id="not-included">
            <div class="card p-6 sm:p-8">
                <h2 class="text-2xl sm:text-3xl font-bold text-center mb-8">Other Places to Explore</h2>
                <p class="text-center text-gray-600 mb-8">This itinerary is packed, but if you have extra time or want to swap an activity, here are other great options in Hyderabad:</p>
                <div class="grid md:grid-cols-2 gap-6">
                    {generate_other_places()}
                </div>
            </div>
        </section>

    </main>

    <footer class="text-center py-8 text-gray-500">
        <p>Itinerary generated by Gemini</p>
    </footer>

    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            feather.replace();

            const tabsContainer = document.getElementById('tabs-container');
            const tabContentContainer = document.getElementById('tab-content');

            // Tab switching logic
            tabsContainer.addEventListener('click', (e) => {{
                if (e.target.classList.contains('tab-button')) {{
                    const day = e.target.dataset.day;
                    
                    // Update button styles
                    tabsContainer.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
                    e.target.classList.add('active');

                    // Show/hide content
                    tabContentContainer.querySelectorAll('.day-content').forEach(content => {{
                        gsap.to(content, {{
                            autoAlpha: 0,
                            y: 10,
                            duration: 0.3,
                            onComplete: () => {{
                                content.classList.add('hidden');
                                if (content.id === `day-${{day}}-content`) {{
                                    content.classList.remove('hidden');
                                    gsap.fromTo(content, {{autoAlpha: 0, y: 10}}, {{autoAlpha: 1, y: 0, duration: 0.3}});
                                }}
                            }}
                        }});
                    }});
                }}
            }});

            // GSAP Animations
            gsap.registerPlugin(ScrollTrigger);
            gsap.from('header', {{ opacity: 0, y: -50, duration: 1, ease: 'power3.out' }});
            
            const cards = gsap.utils.toArray('.card, .cost-summary-grid > div, .travel-option-card');
            cards.forEach(card => {{
                gsap.from(card, {{
                    opacity: 0,
                    y: 50,
                    duration: 0.8,
                    ease: 'power3.out',
                    scrollTrigger: {{
                        trigger: card,
                        start: 'top 90%',
                        toggleActions: 'play none none none'
                    }}
                }});
            }});

            // Final feather replacement after dynamic content is added
            feather.replace();
        }});
    </script>
</body>
</html>
    """
    return html_template

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 3:
        print("Usage: python generate_itinerary.py <input_json_path> <output_html_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
        
        html_content = generate_html(data)
        
        with open(output_path, 'w') as f:
            f.write(html_content)
            
        print(f"Successfully generated HTML file at {output_path}")

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {input_path}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
