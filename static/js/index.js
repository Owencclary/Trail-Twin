const remove_element = document.getElementsByClassName("remove_element")

// Adds an event listener to each activity element to remove it
for (let i = 0; i < remove_element.length; i++) {
    remove_element[i].addEventListener("click", (e) => {
        e.preventDefault();
        const remove_element = e.target.dataset.route;
        console.log(remove_element)
        fetch(remove_element)
        .then(res => res.json()
        .then((data) => {

            console.log(data)
            if (data == "success") {
                e.target.remove();
                conosole.log("Removed " + remove_element_href)
            } else {
                console.log("Failed to remove " + remove_element_href);
            }
        }));
    })
}
