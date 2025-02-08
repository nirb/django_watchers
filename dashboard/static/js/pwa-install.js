let installPromptEvent;

window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault(); // Prevent the default browser prompt
    installPromptEvent = event;

    // Show install button (if you have one in your HTML)
    const installButton = document.getElementById("install-button");
    if (installButton) {
        installButton.style.display = "block";
        installButton.addEventListener("click", () => {
            installPromptEvent.prompt();
        });
    }
});
