<!-- ===================== -->
<!-- README.md TEMPLATE   -->
<!-- ===================== -->

<h1 align="center">Sodium</h1>

<p>
 A fast & reliable vanity sniper for discord server.
</p>

<h2>About the Project:</h2>

<p>
  This project is a <strong>beautiful, high-performance vanity sniper (BETA) </strong>
  <ul>
    <li>Feature 1: Client using websocket</li>
    <li>Feature 2: Unblocked vanity sniping</li>
    <li>Feature 3: Fast & reliable</li>
    <li>Feature 3: Fast & reliable</li>
  </ul>

</p>


<h2>Usage:</h2>

<p>Example of starting the application:</p>

<pre><code>py main.py</code></pre>

<h2>Support me:</h2>
<p>
Before blindly copying the code, please read through it! Making stuff like this takes a while, so please appericate and give me feedback to make my code better!
Also feel free to contribute and do pull requests on this project. People use words like <strong>"Skids"</strong> and such. Please don't be a skid or anything like that
 Be genuine and give me credit, if you don't want to give me credit, then what can I do? haha anyways thanks <3
</p>

<h2>Improve this piece of code:</h2>
<p>The following code can be found in **sodium/src/client.py**</p>
```python
    async def start(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(self.gateway_url, max_msg_size=20 * 1024 * 1024) as ws:
                    await self.send_presence(ws)
                    self.tasks = [self._handle_events(ws)]
                    await asyncio.gather(*self.tasks)
        except Exception as e:
            print(f"Error starting connection: {e}")









