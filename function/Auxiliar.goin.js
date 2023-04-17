// Redirige a una pagina interna
var url = routingContext.request().getParam("url");
routingContext.response().setStatusCode(200).putHeader("Location", url.toString()).end();