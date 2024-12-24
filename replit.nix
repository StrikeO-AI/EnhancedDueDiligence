{pkgs}: {
  deps = [
    pkgs.libGLU
    pkgs.libGL
    pkgs.poppler
    pkgs.poppler_utils
    pkgs.tesseract
    pkgs.glibcLocales
  ];
}
