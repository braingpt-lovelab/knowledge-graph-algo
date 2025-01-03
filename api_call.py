import os
import time
import logging
import asyncio
import tiktoken
from dotenv import load_dotenv
from openai import AzureOpenAI, AsyncAzureOpenAI


def get_num_tokens(sys_prompt, user_prompt):
    enc = tiktoken.encoding_for_model("gpt-4o")
    num_tokens = len(enc.encode(sys_prompt)) + len(enc.encode(user_prompt))
    return num_tokens


def token_cost(input_tokens, output_tokens):
    pricing = {
        "gpt-4o-08-06": {
            "input_token": 2.5/10**6,
            "output_token": 10/10**6
        }
    }
    return pricing['gpt-4o-08-06']['input_token'] * input_tokens + pricing['gpt-4o-08-06']['output_token'] * output_tokens


class MinuteRateLimiter:
    def __init__(self, tokens_per_minute):
        self.tokens_per_minute = tokens_per_minute
        self.tokens_available = tokens_per_minute
        self.last_refill_time = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self, tokens):
        while True:
            async with self.lock:
                now = time.time()
                minutes_passed = (now - self.last_refill_time) / 60.0
                
                # Refill tokens based on time passed
                self.tokens_available = min(
                    self.tokens_per_minute,
                    self.tokens_available + minutes_passed * self.tokens_per_minute
                )
                self.last_refill_time = now

                if self.tokens_available >= tokens:
                    self.tokens_available -= tokens
                    return
            
            # If not enough tokens, wait a bit before checking again
            await asyncio.sleep(1)


rate_limiter = MinuteRateLimiter(tokens_per_minute=100000)


def ask_gpt4(sys_prompt, user_prompt, top_p=1, temperature=0.5):
    logging.info("[ask_gpt4]: Calling Azure OpenAI API")
    load_dotenv()
    
    client = AzureOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        api_version="2024-07-01-preview",
        azure_endpoint=os.getenv("OPENAI_AZURE_ENDPOINT"),
    )

    # Minimal error handling for now
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-2024-08-06",  # deployment name not model name
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt},
            ],
            top_p=top_p,
            temperature=temperature,
        )

    except Exception as e:
       
        logging.error(f"An error occurred while attempting to communicate with Azure OpenAI: {e}")

        return None
    
    return completion.model_dump_json(indent=2)


async def ask_gpt4_async(sys_prompt, user_prompt, top_p=1, temperature=0.5):
    logging.info("[ask_gpt4]: Calling Azure OpenAI API")
    load_dotenv()
    
    client = AsyncAzureOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        api_version="2024-07-01-preview",
        azure_endpoint=os.getenv("OPENAI_AZURE_ENDPOINT"),
    )
    
    await rate_limiter.acquire(get_num_tokens(sys_prompt, user_prompt))

    # Minimal error handling for now
    try:
        completion = await client.chat.completions.create(
            model="gpt-4o-2024-08-06",  # deployment name not model name
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt},
            ],
            top_p=top_p,
            temperature=temperature,
        )

    except Exception as e:
       
        logging.error(f"An error occurred while attempting to communicate with Azure OpenAI: {e}")

        return None
    
    return completion.model_dump_json(indent=2)