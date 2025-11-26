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
    
    def generate_value(self,t:float,pattern:str)->float:
        if pattern=="noise":
            return self.generate_random_noise(base=50.0,variance=5.0)
        elif pattern=="sine_wave":
            return self.generate_sine_wave(t,amplitude=20.0,period=60.0)+50.0
        elif pattern=="linear_trend":
            return self.generate_linear_trend(t,slope=0.1,base=50.0)
        elif pattern=="spike":
            return 50.0+self.generate_spike(probability=0.05,magnitude=100.0)
        elif pattern=="combined":
            value=(
                self.generate_sine_wave(t,amplitude=15.0,period=60.0)+
                self.generate_linear_trend(t,slope=0.05,base=50.0)+
                self.generate_random_noise(base=0.0,variance=3.0)+
                self.generate_spike(probability=0.02,magnitude=80.0)
            )
            return value
        else:
            return self.generate_random_noise(base=50.0,variance=5.0)
        
async def main():
    import argparse

    parser=argparse.ArgumentParser(description="Data Generator for Metric Ingestion Service")
    parser.add_argument(
        "--metric",
        default="test_metric",
        help="Name of the metric to generate",
    )
    parser.add_argument(
        "--pattern",
        choices=["noise","sine_wave","linear_trend","spike","combined"],
        default="sine_wave",
        help="Pattern of the metric to generate",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=300.0,
        help="Duration in seconds to run the generator",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Interval in seconds between metric generations",
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of the Metric Ingestion Service",
    )

    args=parser.parse_args()

    generator=DataGenerator(baseUrl=args.base_url)

    try:
        await generator.continuous_metric_generation(
            metric_name=args.metric,
            pattern=args.pattern,
            duration=args.duration,
            interval=args.interval,
        )
    except KeyboardInterrupt:
        print("Metric generation stopped by user.")
    

if __name__=="main":
    asyncio.run(main())


            
