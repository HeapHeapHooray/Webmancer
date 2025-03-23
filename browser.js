var ws = new WebSocket("ws://127.0.0.1:8765")

ws.addEventListener("open", (event) => {
ws.send("init_session");
console.log("Sending!");
console.log(event);
});
ws.onmessage = function(event) { 
ws.send("Hello Server!");
data = JSON.parse(event.data)
if(data.command == "console_log") {
console.log(data.data)
}
else if(data.command == "alert") {
alert(data.data)
}
else if(data.command == "read_html")
{
                let html =
                    document.getElementsByTagName("html")[0]
                        .innerHTML;
let string = JSON.stringify({"html": html})
ws.send(string)
}
else if(data.command == "get_title")
{
let string = JSON.stringify({"title": document.title})
ws.send(string)
}
else if(data.command == "set_html")
{
document.documentElement.innerHTML = atob(data.data)
}
}
ws.addEventListener("error", (event) => {alert(event.data)})
