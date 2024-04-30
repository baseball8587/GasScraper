import PyPDF2
import re
import json

def get_distributor(pdf_path, start_page):
    extracted_info_list = []
    seen_companies = set()
    retailer_pattern = r"Agway Energy Services|Ambit Energy|American Power & Gas of PA|Constellation Energy|Direct Energy|Dominion Energy Solutions|Energy Rewards|IGS Energy|Just Energy|Major Energy Services|North American Power|NRG Home|Palmco Power PA, LLC|Shipley Energy|WGL Energy"
    phone_pattern = r"1-888-\d{2}-?[A-Za-z]{5}|\d{3}-\d{3}-\d{4}"
    website_pattern = r"www\.\S+?\.(com|net|org|info|edu|gov)(/\S*)?(?=\s|$)"  # Updated pattern to match websites
    retailer_update_pattern = r"Updated\s+\b\w+\s+\d{1,2},\s+\d{4}"
    type_of_price_pattern = r"(Monthly Variable:\nIntroductory Price\nfor First Month)|(Monthly Variable:\nIntroductory Price\nfor New Customers)"


    unwanted_text_pattern = r'''
        Monthly\ssupply\sportion.*?Licensed\sNatural\sGas\sSupplier\sPrices:|
        ◌\s*The\sPrice\sto\sCompare\sis\sthe\sprice\sper\s(therm|ccf).*?if\syou\sdo\snot.*?choose\sa\sgas\ssupplier.*?subject\sto\schange\son\s(January|April|July|October|February|March|May|June|August|September|November|December)\s1.*?All\sother\scharges.*?|
        Natural\sGas\sSupplier\sprices\sare\sfor\sNEW\scustomers.*?Existing\scustomers.*?should\scontact\stheir\ssupplier.*?
    '''

    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            for i in range(start_page - 1, num_pages):
                page = reader.pages[i]
                text = page.extract_text() if page.extract_text() else ""
                text = re.sub(unwanted_text_pattern, '', text, flags=re.DOTALL | re.VERBOSE)

                data = {}
                patterns = {
                    'company_names': r"Columbia Gas of PA, Inc\.|National Fuel Gas|PECO Gas|Philadelphia Gas Works|UGI Utilities, Inc\.|UGI Utilities|Peoples Natural: Equitable Division|Peoples Gas (Formerly Peoples TWP)|Peoples Natural: Peoples Division|Peoples Natural: Peoples Division Residential Servic|Peoples Gas (Formerly Peoples TWP)",
                    'service_types': r"Residential Sales Service|Residential Service|General Service - Residential|Residential Sales",
                    'phone_number': r"\d{1}-\d{3}-\d{3}-\d{4}",
                    'rate_type': r"Rate\s+\w+",
                    'website': r"www\.\S+?\.(com|net|org|info|edu|gov)(/\S*)?",
                    'price_to_compare': r"(?:Price to Compare)\s*(\S+\s+\d{1,2},\s+\d{4})|\$(?!\s*No FFixed Price through)(\s*[^\d$]*?(\d{1,2},\s+\d{4}))",
                    'price': r"(\d{2}\.\d{3})\s*\u00a2|(\d+\.\d+)\s\s*\$|\$\d+\.\d{4}\s+per\s+Mcf"
                }

                for key, pattern in patterns.items():
                    match = re.search(pattern, text)
                    if match:
                        data[key] = match.group(0).strip()
                        text = re.sub(re.escape(match.group(0)), '', text, flags=re.IGNORECASE)  # Remove the matched text immediately

                # Each of these features needs to check if match is found before attempting to extract or modify text
                retailer_match = re.search(retailer_pattern, text)
                if retailer_match:
                    data['retailer_name'] = retailer_match.group(0)
                    text = re.sub(re.escape(retailer_match.group(0)), '', text, count=1)

                phone_match = re.search(phone_pattern, text)
                if phone_match:
                    data['retailer_phone'] = phone_match.group(0)
                    text = text[text.index(phone_match.group(0)) + len(phone_match.group(0)):]

                website_match = re.search(website_pattern, text)
                if website_match:
                    data['retailer_website'] = website_match.group(0)
                    text = re.sub(re.escape(website_match.group(0)), '', text, count=1)

                retailer_update_match = re.search(retailer_update_pattern, text)
                if retailer_update_match:
                    data['retailer_update'] = retailer_update_match.group(0)
                    text = re.sub(re.escape(retailer_update_match.group(0)), '', text, count=1)

                type_of_price_match = re.search(type_of_price_pattern, text)
                if type_of_price_match:
                    data['TypeofPrice'] = type_of_price_match.group(0)
                    text = re.sub(re.escape(type_of_price_match.group(0)), '', text, count=1)

                if 'company_names' in data and 'service_types' in data:
                    company_service_pair = (data['company_names'], data['service_types'])
                    if company_service_pair not in seen_companies:
                        seen_companies.add(company_service_pair)
                        page_data = {
                            "Company Name": company_service_pair[0],
                            "Service": company_service_pair[1],
                            "Phone Number": data.get('phone_number', "Not found"),
                            "Rate Type": data.get('rate_type', "Not found"),
                            "Website": data.get('website', "Not found"),
                            "Price to Compare Through": data.get('price_to_compare', "Not found").strip("Price to Compare  \n ").strip("$        "),
                            "Price": data.get('price', "Not found").strip(" $").strip("  \u00a2").strip(" per Mcf"),
                            "Retailer Details": {
                                "Retailer Name": data.get('retailer_name', "Not found"),
                                "Retailer Phone": data.get('retailer_phone', "Not found"),
                                "Retailer Website": data.get('retailer_website', "Not found"),
                                "Retailer Update": data.get('retailer_update', "Not found").strip("Updated "),
                                "FixedOrVar":data.get('FixedOrVar',"Not found"),
                                "TypeOfPrice":data.get('TypeofPrice',"Not found").replace("\n"," "),
                                "Remaining Text": text.strip()
                            }
                        }
                        extracted_info_list.append(page_data)

        return json.dumps(extracted_info_list, indent=4)  # Return JSON formatted string
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Path to the PDF file and extraction start
pdf_path = "/Users/colinjacobs/Desktop/fun/Capstone/Equitable-Energy/OCA/gas/uploads/gas_december2017.pdf"
extracted_data = get_distributor(pdf_path, 6)
print(extracted_data)
