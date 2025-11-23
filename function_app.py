import azure.functions as func
import logging
import os
import msal
import requests
import json
from datapizza.clients.openai import OpenAIClient
from datapizza.tracing import ContextTracing

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

sector = [
    "Real Estate",
    "Power Chemicals, Metals & Mining",
    "Financial Institutions",
    "Energy & Commodities",
    "Transport & Industry",
    "Public Sector",
    "Consumer Retail & Health",
    "Tech", 
    "Media", 
    "Telecom"
]

issue = [
    "Waste",
    "Governance",
    "Reporting/disclosure requirements",
    "Natural disasters",
    "risk management",
    "Climate",
    "Biodiversity",
    "Social",
    "Pollution",
    "equal opportunities",
    "Transparency",
    "working conditions",
    "bribery",
    "business conduct",
    "human rights",
    "Energy",
    "lobbying",
    "data security",
    "Greenwashing",
    "conflict of interest",
    "data security and resilience",
    "supply chain",
    "labor rights",
    "fraud",
    "pricing",
    "corruption",
    "accesssibility",
    "land grabbing",
    "health",
    "health and human rights",
    "AI",
    "Renewable energy",
    "Plastic",
    "ESG backlash",
    "data protection"
]

RISK_DRIVER = [
    "Climate Risk",
    "Transition Risk",
    "Environmental Risk",
    "Physical and Transition Risk",
    "Physical Risk",
    "Social Risk",
    "Governance Risk"
]

GEOGRAPHY = [
    "UNITED KINGDOM OF GREAT BRITAIN",
    "EUROPEAN UNION",
    "WORLDWIDE",
    "UNITED STATES OF AMERICA",
    "NETHERLANDS",
    "FRANCE",
    "DENMARK",
    "SWITZERLAND", 
    "GERMANY",
    "POLAND",
    "SPAIN",
    "ITALY",
    "BRAZIL",
    "NORWAY",
    "FINLAND",
    "CZECHIA",
    "ROMANIA",
    "IRELAND",
    "SWEDEN",
    "AUSTRIA",
    "LUXEMBOURG"
]

TIME_HORIZON = [
    "Long term (>5 years)",
    "Short term (1-3 years)",
    "Medium term (3-5 years)"
]

LIKELIHOOD = [
    "Moderate",
    "Major",
    "Minor"
]

SEVERITY = [
    "Major",
    "Moderate", 
    "No impact",
    "Minor"
]

IDIOSYNCRASY = [
    "Systematic",
    "Idiosyncratic"
]

def get_promt(text_input, dimensions):
    return f"""
    Perform a comprehensive policy and market analysis of the provided text. Your response must be a structured JSON with the following requirements:

    1. Issue Type:
    - Identify a SINGLE, precise issue from this comprehensive list:
        {issue}
    - Provide a concise, one-sentence justification for your selection that directly links to the text's content

    2. Summary:
    - Provide a concise, objective summary of the key policy changes
    - Highlight the most significant implications for the energy and housing sectors
    - Maximum 150 words

    3. Policy Dimensions: 
    - Select ONE most appropriate dimension from these options: 
        {dimensions}
    - Justify your choice with a brief explanation

    4. Affected Sectors:
    - Identify one to two relevant sectors from this list: 
        {sector}
    - For each identified sector, provide a one-sentence rationale for its inclusion

    5. Strategic Insights:
    - Offer 2-3 key strategic considerations for policymakers or businesses based on these regulatory changes

    6. Relevancy:
    - Offer insight on how relevant this article is for a bank / financial institution with customers from this industry

    7. Additional Categorizations:
    - Time Horizon: Select the most appropriate option
        Options: {TIME_HORIZON}
        Justify your selection based on the policy's long-term implications

    - Likelihood: Assess the potential implementation or impact
        Options: {LIKELIHOOD}
        Provide a rationale for your assessment

    - Severity: Evaluate the potential market and policy impact
        Options: {SEVERITY}
        Explain the reasoning behind your severity rating

    - Risk Driver: Identify the primary type of risk highlighted
        Options: {RISK_DRIVER}
        Elaborate on how this risk type is manifested in the text

    - Geography: Identify the affected regions and countries
        Options: {GEOGRAPHY}

    - Idiosyncrasy: Identify, whether this article may impose idiosyncratic or systematic risks
        Options : {IDIOSYNCRASY}

    Text to analyze: {text_input}

    """

def load(text):
    try:
        endpoint = "https://d-oai-hsw-int-makeathon-01.openai.azure.com/openai/v1"
        model_name = "gpt-5-pro-2"

        subscription_key = os.environ.get('MakeathonModelAccessKey')

        client = OpenAIClient(
            api_key=subscription_key,
            base_url=endpoint,
            model=model_name
        )
        with ContextTracing().trace("my_operation"):
            response = client.invoke(get_promt(text))
        return response.text
    except Exception as e:
        print(e)

@app.route("sample_http_trigger")
def sample_http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    TENANT_ID = os.environ.get("TENANT_ID")
    RESOURCE_URL = os.environ.get("RESOURCE_URL")
    AUTHORITY_URL = f"https://login.microsoftonline.com/{TENANT_ID}"

    azure_app = msal.ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=AUTHORITY_URL
    )

    result = azure_app.acquire_token_for_client(scopes=[f"{RESOURCE_URL}/.default"])

    if "access_token" in result:
        access_token = result['access_token']
        
        # --- 3. Define Request Parameters ---
        headers = {
            'Authorization': f'Bearer {access_token}',
            'OData-MaxVersion': '4.0',
            'OData-Version': '4.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=utf-8',
            'Prefer': 'odata.include-annotations="*"',
        }
        
        # Example: Fetch the first 10 accounts
        api_url = f"{RESOURCE_URL}api/data/v9.2/ecofact_ecbdimensions?$select=ecofact_name"
        # --- 4. Make the Request ---
        print(api_url)
        response = requests.get(api_url, headers=headers)
        ecbdimensions = []
        json_data = json.loads(response.text)
        for item in json_data["value"]:
            ecbdimensions.append(item["ecofact_name"])
        print(ecbdimensions)
        text_1 = """The European Commission welcomes the adoption by EU Member States of the 19th package of sanctions against Russia. The new package of sanctions substantially increases the pressure on the Russian war economy, targeting key sectors such as energy, finance, the military industrial base, special economic zones, as well as enablers and profiteers of its war of aggression.\n\nA total ban on Russian Liquefied Natural Gas (LNG) and a further clamp-down on the shadow fleet represent the strongest sanctions yet on Russia's crucial energy sector. Strong measures also target financial services and infrastructure (including for the first time crypto), as well as trade. The measures also target the services sector and strengthen anti-circumvention tools. With this package, the number of listed vessels in Russia's shadow fleet reaches a total of 557.\n\nThe 19th package contains the following key elements:\n\nENERGY MEASURES\n\nBan on imports of Russian liquefied natural gas (LNG) as of 1 January 2027 for long-term contracts, and within six months as of the entry into force of the sanctions for short-term contracts.\n\nFull transaction ban on major companies Rosneft and Gazprom Neft: The new measures eliminate the exemption for Rosneft's and Gazprom Neft's oil and gas imports into the EU. The import of oil from third countries, such as Kazakhstan, and the transport of oil compliant with the Oil Price Cap to third countries, are exempted.\n\nThe EU is also taking measures against important third country operators enabling Russia's revenue streams. This involves sanctioning Chinese entities - two refineries and an oil trader - that are significant buyers of Russian crude oil.\n\nImport ban on a variant of liquefied petroleum gas (LPG): This measure addresses circumvention, as some Member States report that this variant has been used to bypass existing LPG restrictions.\n\n117 additional vessel listings: With these new listings, a total of 557 vessels in Russia's shadow fleet are now listed by the EU. They are subject to a port access ban and a ban on receiving services. The EU continues conducting outreach to flag states to ensure that ship registers do not allow these tankers to sail under their flag.\n\nAdditional sanctions are notably imposed across the shadow fleet value chain, including on Litasco Middle East DMCC, Lukoil's prominent shadow fleet enabler based in the UA, as well as on maritime registries providing false flags to shadow fleet vessels. In addition, 2 oil trading companies in Hong Kong and the United Arab Emirates (UAE) are added to the scope of the transaction ban.\n\nExtension of the port infrastructure ban: This will enable the EU to list ports in third countries that are instrumental to the Russian war effort.\n\nThe new measures also include additional prohibitions on energy-related services, such as scientific and technical services (for example, geological prospecting and mapping).\n\nFINANCIAL MEASURES\n\nBanking: 5 new banks in Russia are added to the transaction ban. No EU operator will be able to engage with any of the listed banks directly or indirectly.\n\nPayments: new bans on Russia's payment card and fast payment system (Mir and SBP). The measures also list 4 new financial institutions in Belarus and Kazakhstan that use the Russian payments system (SPFS).\n\nCryptocurrencies and exchanges: The EU is imposing full-fledged sanctions on the developer of a widely used rouble-backed stablecoin A7A5, the Kyrgyz issuer of that coin, and a related major trading platform. For the first time, the new measures also prohibit the use of that cryptocurrency. In addition, the sanctions directly target a cryptocurrency exchange in Paraguay that has played a key role in circumventing existing restrictions. This step marks a significant evolution in the EU's sanctions regime. By addressing the use of stablecoins and offshore exchanges, the EU aims to close loopholes and reinforce the integrity of its financial sanctions framework.\n\nCrypto services: EU operators are banned from providing crypto services and certain fintech services that enable Russia to develop its own financial infrastructure and possibly circumvent sanctions.\n\nTransactions: The package introduces transaction bans on 5 third-country banks in Central Asia that support Russia's war economy and frustrate the effectiveness of our sanctions. EU operators are banned from carrying out transactions with any of those financial operators.\n\nTRADE MEASURES\n\nThe package expands export restrictions and bans to further disrupt and weaken Russia's military-industrial complex. These include:\n\nIndividual sanctions (‘listings') of businesspersons and companies forming part of the Russian military-industrial complex, and operators from UAE and China producing or supplying military and dual-use goods to Russia.\n\nNew export restrictions on additional dual-use items and advanced technologies, including metals for the construction of weapon systems and products used in the preparation of propellants, not yet under sanctions.\n\nNew export bans on items such as salts and ores, constructions materials and articles of rubber, corresponding to a value of EUR 155 million of EU exports in 2024 prices.\n\nANTI-CIRCUMVENTION MEASURES\n\nThis package adds 45 entities to the list of those providing direct or indirect support to Russia's military industrial complex or engaged in sanctions circumvention. This includes 28 established in Russia and 17 in third countries (12 in China, including Hong Kong, 3 in India and 2 in Thailand).\n\nADDITIONAL LISTINGS\n\nToday's package contains 69 additional listings. They are now subject to asset freezes and the prohibition to make funds and economic resources available to them, and – in the case of individuals – also to travel bans. These listings include oligarchs, Russian energy companies, a large Russian company involved in gold production, a Russian company managing the shadow fleet, one petrochemical company and one refinery in China facilitating oil trade with Russia, a large Chinese State owned company, other legal and natural persons. The EU is reinforcing accountability of those involved in abduction, forced assimilation and indoctrination of Ukrainian children. Therefore, today's listings include 11 additional individuals involved in such activities. In order to streamline future sanctions on persons responsible for the abduction, forced assimilation and militarised education of Ukrainian minors, the Council is also introducing a new listing criterion.\n\nOTHER MEASURES\n\nMeasures targeting Russia's Special Economic Zones (SEZs): These zones are designed to attract foreign investment and play a critical role in driving economic growth and infrastructure development. To make it clear that EU businesses should stay away, the package proposes a prohibition on entering into new contracts with any entity established within certain Russian SEZs. In addition, two of these SEZs – Alabuga and Technopolis Moscow – will be subject to a ban that applies also to existing contracts. This decision – essentially forcing divestment – reflects the documented focus of these two zones on activities that contribute to the war effort.\n\nService bans: As part of the new measures, the EU introduces service bans blocking Russian access to advanced digital capabilities within the Union, including certain space-based services and AI services. In parallel, the existing targeted ban on services to the Russian government will be reinforced. A new requirement for prior authorisation will apply to any non-prohibited services to the Russian government, ensuring that all such activities are subject to strict scrutiny and oversight.\n\nProhibition of re-insurance: The new measures prohibit re-insurance services regarding vessels and aircraft of the Russian government or Russian persons for up to five years after their sale to third countries.\n\nRussian diplomats: The new measures introduce an obligation for Russian diplomats, travelling across the EU beyond their country of accreditation, to inform the relevant EU Member State in advance. EU Member States may impose an authorisation requirement on Russian diplomats for traveling to their territories, based on visas or residence permits issued by another state. This measure is meant to tackle the increasingly hostile intelligence activities that support Russia's aggression against Ukraine."""
        if response.status_code == 200:
            return func.HttpResponse(
                "Successfully connected to Dynamics 365.",
                status_code=200
            )
        else:
            return func.HttpResponse(
                f"Request failed with status code: {response.status_code}",
                status_code=response.status_code
            )
    else:
        return func.HttpResponse(
                f"Failed to acquire token. Error Description: {result.get("error_description")}",
                status_code=400
            )
    

