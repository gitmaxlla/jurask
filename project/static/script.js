const status_message =  document.getElementById("status");
const answer_text = document.getElementById("answer-text");
const references = document.getElementById("references");


document.getElementById("submit").onclick = () => {
    send_query();
}

document.getElementById("input").oninput = function() {
    var reference_wrapper = document.getElementById("input-measure-wrapper");
    var reference = document.getElementById("input-width-measure");

    reference_wrapper.style.maxWidth = this.offsetWidth + "px";
    reference.innerText = this.innerText;
    this.style.width = reference.offsetWidth + 20 + "px";
}

async function send_query() {
    answer_text.innerText = '';
    references.innerHTML = '';

    status_message.classList.remove("none");
    input = document.getElementById("input").innerText;
    status_message.innerText = "Загрузка...";

    fetch("/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json;charset=utf-8"
        },
        body: JSON.stringify({"contents": input})
    }).then((response => response.json())).then(answer => {
        if (Object.keys(answer.articles).length === 0) {
            status_message.innerText = "Вопрос не относится к Конституции РФ, либо был обработан системой с ошибкой. Попробуйте перефразировать ваш вопрос и задать его снова.";
        } else {
            display_answer(answer);
        }
    })
}

function display_referenced_documents(referenced_articles) {
    status_message.classList.add("none");

    for (const [article_name, article_text] of Object.entries(referenced_articles)) {
        const reference_name = document.createElement("button");
        reference_name.className = "referenced-article-btn";
        reference_name.innerText = article_name;

        const reference_text = document.createElement("div");
        reference_text.className = "referenced-article-text none";
        reference_text.innerText = article_text;
        
        reference_name.addEventListener("click", function() {
            this.classList.toggle("is-expanded");
            var text = this.nextElementSibling;
        
            if (text.classList.contains("none")) {
                text.classList.remove("none")
            } else {
                text.classList.add("none")
            }
        });

        references.appendChild(reference_name);
        references.appendChild(reference_text)
    }
}

function display_answer(response) {
    document.getElementById("answer").classList.remove("hidden");
    answer_text.innerText = response.answer;
    display_referenced_documents(response.articles)
}