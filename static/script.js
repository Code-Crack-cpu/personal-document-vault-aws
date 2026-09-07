const fileInput = document.querySelector("#file");
const fileName = document.querySelector("#file-name");
if (fileInput && fileName) {
  fileInput.addEventListener("change", () => {
    fileName.textContent = fileInput.files.length
      ? fileInput.files[0].name
      : "PDF, JPG, JPEG or PNG · Maximum 10 MB";
  });
}
