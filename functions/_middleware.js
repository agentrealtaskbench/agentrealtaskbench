// Send the old pages.dev address and www to the canonical domain.
// Preview deployments (<hash>.agentrealtaskbench.pages.dev, <branch>.…) are left alone.
const CANONICAL = "agentrealtaskbench.ai";
const REDIRECT_HOSTS = new Set(["agentrealtaskbench.pages.dev", "www.agentrealtaskbench.ai"]);

export async function onRequest(context) {
  const url = new URL(context.request.url);
  if (REDIRECT_HOSTS.has(url.hostname)) {
    url.hostname = CANONICAL;
    url.protocol = "https:";
    return Response.redirect(url.toString(), 301);
  }
  return context.next();
}
