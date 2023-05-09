// Redirige a una pagina externa (con token)
var url = routingContext.request().getParam("url");
var token = routingContext.request().getParam("access_token");
if (token != "") url += "?access_token=" + token;
routingContext.response().setStatusCode(200).putHeader("Location", url.toString()).end();