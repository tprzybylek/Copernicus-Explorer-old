$(document).ready(function () {
    $("tr, path").hover(function () {
        var selectedClass = "." + $(this).attr('class').split(' ')[0];
        $(selectedClass).toggleClass("selected");
    });

    IDs = Cookies.get('IDs')
    if (IDs) {
        var IDs = JSON.parse(IDs);
        $(".itemCount").text("(" + IDs.length + ")")
    }

    $(".removeFromCart").click(function () {
        var ID = $(this).attr("id");

        var index = IDs.indexOf(ID);

        if (IDs && index > -1) {
            IDs.splice(index, 1);
        };

        Cookies.set('IDs', JSON.stringify(IDs));
        $(".itemCount").text("(" + IDs.length + ")")
        $('.' + ID).remove();
    });

    $(".addToCart").click(function () {
        var ID = $(this).attr("id");
        IDs = Cookies.get('IDs')
        if (IDs) {
            var IDs = JSON.parse(IDs);
            IDs.push(ID);
        } else {
            var IDs = [ID];
        };
        Cookies.set('IDs', JSON.stringify(IDs));
        $(".itemCount").text("(" + IDs.length + ")")
    });

});