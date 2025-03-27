const status_message =  document.getElementById("status");
const answer_text = document.getElementById("answer-text");
const references = document.getElementById("references");


document.getElementById("input").oninput = function() {
    var reference_wrapper = document.getElementById("input-measure-wrapper");
    var reference = document.getElementById("input-width-measure");

    reference_wrapper.style.maxWidth = this.offsetWidth + "px";
    reference.innerText = this.innerText;
    this.style.width = reference.offsetWidth + 20 + "px";
}

async function send_query(element) {
    answer_text.innerText = '';
    references.innerHTML = '';

    status_message.classList.remove("none");
    input = document.getElementById("input").value;
    status_message.innerText = "Загрузка...";


    await new Promise(r => setTimeout(r, 2000));
    display_answer({"answer": "Права граждан Российской Федерации гарантированы Конституцией Российской Федерации. Согласно статье 17, права и свободы человека и гражданина неотчуждаемы и принадлежат каждому от рождения. Граждане Российской Федерации имеют право участвовать в управлении делами государства, избирать и быть избранными в органы государственной власти и местного самоуправления, участвовать в референдуме (статья 32). Кроме того, граждане имеют право на свободное передвижение, выбор места пребывания и жительства, а также право выезжать за пределы Российской Федерации и возвращаться в Российскую Федерацию (статья 27). Все граждане равны перед законом и судом, и государство гарантирует равенство прав и свобод человека и гражданина независимо от различных обстоятельств (статья 19).", "references": {"Глава 2. Права и свободы человека и гражданина. Статья 17": "1. В Российской Федерации признаются и гарантируются права и свободы человека и гражданина согласно общепризнанным принципам и нормам международного права и в соответствии с настоящей Конституцией. 2. Основные права и свободы человека неотчуждаемы и принадлежат каждому от рождения. 3. Осуществление прав и свобод человека и гражданина не должно нарушать права и свободы других лиц.", "Глава 2. Права и свободы человека и гражданина. Статья 32": "1. Граждане Российской Федерации имеют право участвовать в управлении делами государства как непосредственно, так и через своих представителей. 2. Граждане Российской Федерации имеют право избирать и быть избранными в органы государственной власти и органы местного самоуправления, а также участвовать в референдуме. 3. Не имеют права избирать и быть избранными граждане, признанные судом недееспособными, а также содержащиеся в местах лишения свободы по приговору суда. 4. Граждане Российской Федерации имеют равный доступ к государственной службе. 5. Граждане Российской Федерации имеют право участвовать в отправлении правосудия.", "Глава 2. Права и свободы человека и гражданина. Статья 27": "1. Каждый, кто законно находится на территории Российской Федерации, имеет право свободно передвигаться, выбирать место пребывания и жительства. 2. Каждый может свободно выезжать за пределы Российской Федерации. Гражданин Российской Федерации имеет право беспрепятственно возвращаться в Российскую Федерацию.", "Глава 2. Права и свободы человека и гражданина. Статья 19": "1. Все равны перед законом и судом. 2. Государство гарантирует равенство прав и свобод человека и гражданина независимо от пола, расы, национальности, языка, происхождения, имущественного и должностного положения, места жительства, отношения к религии, убеждений, принадлежности к общественным объединениям, а также других обстоятельств. Запрещаются любые формы ограничения прав граждан по признакам социальной, расовой, национальной, языковой или религиозной принадлежности. 3. Мужчина и женщина имеют равные права и свободы и равные возможности для их реализации."}});

    // let response = fetch("/", {
    //     method: "POST",
    //     headers: {
    //         "Content-Type": "application/json;charset=utf-8"
    //     },
    //     body: JSON.stringify({"contents": input})
    // }).then((response => response.json())).then(answer => {
    //     display_answer(answer);
    // })
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
    display_referenced_documents(response.references)
}