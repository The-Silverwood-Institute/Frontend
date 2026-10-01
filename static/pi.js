const piMark = document.getElementById("pi-mark");

if (piMark) {
  let clicks = 0;

  piMark.addEventListener("click", () => {
    clicks += 1;
    if (clicks >= 3) {
      window.location.assign("/debug");
    }
  });
}
