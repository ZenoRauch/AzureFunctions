import os
from datapizza.clients.openai import OpenAIClient
from datapizza.tracing import ContextTracing
import logging

class Caller:
    def get_promt(self, text_input, required_values):
        return f"""
        Perform a comprehensive policy and market analysis of the provided text. Your response must be a structured JSON with the following requirements:

        1. Issue Type:
        - Identify a SINGLE, precise issue from this comprehensive list:
            {required_values[0]}
        - Provide a concise, one-sentence justification for your selection that directly links to the text's content

        2. Summary:
        - Provide a concise, objective summary of the key policy changes
        - Highlight the most significant implications for the energy and housing sectors
        - Maximum 150 words

        3. Policy Dimensions: 
        - Select ONE most appropriate dimension from these options: 
            {required_values[1]}
        - Justify your choice with a brief explanation

        4. Affected Sectors:
        - Identify one to two relevant sectors from this list: 
            {required_values[2]}
        - For each identified sector, provide a one-sentence rationale for its inclusion

        5. Strategic Insights:
        - Offer 2-3 key strategic considerations for policymakers or businesses based on these regulatory changes

        6. Relevancy:
        - Offer insight on how relevant this article is for a bank / financial institution with customers from this industry

        7. Additional Categorizations:
        - Time Horizon: Select the most appropriate option
            Options: {required_values[3]}
            Justify your selection based on the policy's long-term implications

        - Likelihood: Assess the potential implementation or impact
            Options: {required_values[4]}
            Provide a rationale for your assessment

        - Severity: Evaluate the potential market and policy impact
            Options: {required_values[5]}
            Explain the reasoning behind your severity rating

        - Risk Driver: Identify the primary type of risk highlighted
            Options: {required_values[6]}
            Elaborate on how this risk type is manifested in the text

        - Geography: Identify the affected regions and countries
            Options: {required_values[7]}

        - Idiosyncrasy: Identify, whether this article may impose idiosyncratic or systematic risks
            Options : {required_values[8]}

        Text to analyze: {text_input}

        """
        
    async def load(self, text, required_values):
        
        endpoint = "https://d-oai-hsw-int-makeathon-01.openai.azure.com/openai/v1"
        model_name = "gpt-5-pro-2"

        subscription_key = os.environ.get('MakeathonModelAccessKey')

        client = OpenAIClient(
            api_key=subscription_key,
            base_url=endpoint,
            model=model_name
        )
        logging.info("hello world")
        with ContextTracing().trace("my_operation"):
            response = await client.invoke(self.get_promt(text, required_values))
        try:
            final_response_text = await response.text()
            logging.info(final_response_text)
            
            # Return the final text string
            return final_response_text
            
        except AttributeError:
            # If .text() isn't the method, try .json() or .read() based on your client's documentation
            logging.error("Could not find the .text() method. Check your OpenAIClient documentation.")
            return None
        