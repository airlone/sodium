from client import *
from console import *
from headers import *
from pretty import *
import asyncio

console = GradientConsole((255, 0, 0), (0, 0, 255))

async def main(): 
    targets = {}
    GradientConsole.clear()
    for t in open("inputs/targets.txt").read().splitlines():
        if t != "":
            guid = Client.fetch_guild_id(t.strip())
            if guid != None:
                targets[guid] = t
                console.println("Fetched GUILD ID: " + guid + " from -> " + t)

    time.sleep(1)

    data = json.load(open("inputs/config.json", 'r', encoding='UTF-8'))

    cl = Client(
        token=data["token"], 
        targets=targets, 
        guid=data["guild_id"], 
        password=data["password"],
        console=console
    )
    GradientConsole.clear()

    await cl.start()

if __name__ == "__main__":
    asyncio.run(main())
    

    


    

    
