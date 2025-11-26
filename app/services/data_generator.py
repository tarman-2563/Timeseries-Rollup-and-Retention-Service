import random
import math
import asyncio
from datetime import datetime
import httpx
from typing import Optional


class DataGenerator:
    def __init__(self,baseUrl:str=None):
        self.baseUrl=baseUrl or "http://default-url.com"

    def generate_random_noise(self,base:float,variance:float)->float:
        return base+random.uniform(-variance,variance)
    
    def generate_sine_wave(self,t:float,amplitude:float,period:float)->float:
        return amplitude*math.sin(2*math.pi*t/period)
    
    def generate_linear_trend(self,t:float,slope:float,base:float)->float:
        return base+slope*t
    
    def generate_spike(self,probability:float,magnitude:float):
        if random.random()<probability:
            return magnitude
        return 0.0
    
    async def continuous_metric_generation(self,metric_name:str="test",pattern:str="sine_wave",duration:float=50.0,interval:float=1.0):
        print(f"Starting metric generation for {metric_name} with pattern {pattern}")
        print(f"Data will be sent to {self.baseUrl}/metrics/ingest every {interval} seconds for {duration} seconds.")

        startTime=datetime.now()
        count=0

        async with httpx.AsyncClient() as client:
            while True:
                if duration and (datetime.now()-startTime).total_seconds()>=duration:
                    print("Duration reached, stopping metric generation.")
                    break

                t=(datetime.now()-startTime).total_seconds()
                value=self.generate_value(t,pattern)

                metric_data={
                    "metric_name":metric_name,
                    "value":value,
                    "timestamp":datetime.now().isoformat(),
                    "labels":{"pattern":pattern,"generator":"DataGenerator"}
                }

                try:
                    response=await client.post(f"{self.baseUrl}/metrics/ingest",json=metric_data,timeout=5.0)

                    if response.status_code==200:
                        count+=1
                        if count%10==0:
                            print(f"Sent {count} metrics so far...")
                    else:
                        print(f"Failed to send metric: {response.status_code} - {response.text}")
                
                except Exception as e:
                    print(f"Error sending metric: {str(e)}")

                await asyncio.sleep(interval)


            
