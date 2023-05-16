document.addEventListener("DOMContentLoaded", function () {
  var btn = document.getElementById("add-task-btn");
  btn.addEventListener("click", function () {
    var taskDescription = document.getElementById("task-description").value;
    console.log("task description fetched - !" + taskDescription);

    fetch("/generate-task-steps", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ description: taskDescription }),
    })
      .then((response) => response.json())
      .then((data) => {
        var taskList = document.getElementById("task-list");
        taskList.innerHTML = "";
        data.tasks.forEach(function (task) {
          var li = document.createElement("li");
          li.className =
            "list-group-item d-flex justify-content-between align-items-center";

          var btn = document.createElement("button");
          btn.className = "btn btn-add";
          btn.style.background = "transparent";
          btn.style.border = "none";
          btn.style.color = "black";
          btn.appendChild(document.createTextNode("+"));
          btn.addEventListener("click", addButtonListener);

          var p = document.createElement("p");
          p.className = "mb-0 top-parag";
          p.textContent = task;

          var right_div = document.createElement("div");
          right_div.className = "w-90";
          right_div.id = "right-div";
          right_div.style = "width: 100%";
          right_div.appendChild(p);

          var left_div = document.createElement("div");
          left_div.className = "w-10";
          left_div.appendChild(btn);

          li.appendChild(right_div);
          li.appendChild(left_div);

          taskList.appendChild(li);
        });
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  });
});

function addButtonListener() {
  var li = this.parentElement.parentElement;
  var top_p = li.querySelector(".w-90").querySelector(".top-parag");
  fetch("/more-info-of-step", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ step: top_p.textContent }),
  })
    .then((response) => response.json())
    .then((data) => {
      var hr = document.createElement("hr");
      hr.style.width = "90%";
      hr.style.margin = "0 auto";

      var p = document.createElement("p");
      p.className = "mb-0 mt-3 bottom-parag";
      p.textContent = data.moreInfo;

      var left_div = this.parentElement.parentElement.querySelector(".w-90");

      top_p = left_div.querySelector(".top-parag");
      top_p.style =
        "height: 52px; display: flex; align-items: center; justify-content: center; width: 100%; ";

      left_div.appendChild(hr);
      left_div.appendChild(p);

      btn = this.parentElement.parentElement
        .querySelector(".w-10")
        .querySelector(".btn-add");
      btn.className = "btn btn-minus";
      btn.innerHTML = "";
      btn.appendChild(document.createTextNode("-"));
      btn.removeEventListener("click", addButtonListener);
      btn.addEventListener("click", minusButtonListener);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

function minusButtonListener() {
  btn = this;
  btn.className = "btn btn-add";
  btn.innerHTML = "";
  btn.appendChild(document.createTextNode("+"));
  btn.removeEventListener("click", minusButtonListener);
  btn.addEventListener("click", addButtonListener);

  var left_div = this.parentElement.parentElement.querySelector(".w-90");

  var elements = left_div.getElementsByClassName("bottom-parag");

  elements = Array.from(elements);
  for (var i = 0; i < elements.length; i++) {
    elements[i].remove();
  }

  var children = left_div.children;
  for (var i = 0; i < children.length; i++) {
    var child = children[i];
    if (child.tagName === "HR") {
      left_div.removeChild(child);
      // Decrement the counter as the childNodes array has been modified
      i--;
    }
  }
}
