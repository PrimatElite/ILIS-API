$(document).ready(function() {
    $("body").tooltip({ selector: '[data-role=tooltip]' });
});

$("#token-field").on("mousedown", function(event) {
    event.preventDefault();
});

var tokenIcon = $("#token-icon");

function updateTooltipPos() {
    var tooltip = $("#token-tooltip");
    var iconPos = tokenIcon.position();
    tooltip.css({ left: (iconPos.left + 4 + (tokenIcon.width() - tooltip.width()) / 2) + "px" });
    tooltip.css({ top: (iconPos.top - 2 - tooltip.height()) + "px" });
}

tokenIcon.on("mouseover", function() {
    updateTooltipPos();
});

tokenIcon.on("click", function() {
    var input = $("#token-field");
    var tmp = $("<input>");
    $("body").append(tmp);
    tmp.val(input.val()).select();
    var successful = document.execCommand("copy");
    tmp.remove();
    if (successful) {
        $("#token-tooltip-inner").html("Copied to clipboard");
    } else {
        $("#token-tooltip-inner").html("Failed to copy");
    }
    updateTooltipPos();
});

tokenIcon.on("mouseout", function() {
    $("#token-tooltip-inner").html("Copy to clipboard");
});
