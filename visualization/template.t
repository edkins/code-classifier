<html>
<head>
<meta charset="utf-8">
<script>
"use strict";

const data = {{data}};

function mouseover(event) {
    const label = event.target.dataset.label;
    const bg = document.getElementById('bg');
    bg.innerHTML = '';
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', event.target.getAttribute('x'));
    text.setAttribute('y', parseFloat(event.target.getAttribute('y')) + 50);
    text.textContent = label;
    text.setAttribute('font-size', 30);
    text.setAttribute('fill', '#f00');
    bg.appendChild(text);
}

function load() {
    const svg = document.getElementById('fg');
    const n = data.x.length;
    const hw = svg.getAttribute('width') / 2;
    const hh = svg.getAttribute('height') / 2;
    const show_text = true;
	svg.innerHTML = '';
    let max = 0;
    for (let i = 0; i < n; i++) {
        max = Math.max(max, Math.abs(data.x[i] / hw), Math.abs(data.y[i] / hh));
    }
    const scale = 0.9 / max;
    for (let i = 0; i < n; i++) {
        if (show_text) {
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            circle.setAttribute('x', hw + scale * data.x[i]);
            circle.setAttribute('y', hh + scale * data.y[i]);
            circle.setAttribute('font-size', 5);
            circle.textContent = data.labels[i];
            circle.dataset.label = data.labels[i];
            circle.onmouseover = mouseover;
            svg.appendChild(circle);
        } else {
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', hw + scale * data.x[i]);
            circle.setAttribute('cy', hh + scale * data.y[i]);
            circle.setAttribute('r', 4);
            circle.dataset.label = data.labels[i];
            circle.onmouseover = mouseover;
            svg.appendChild(circle);
        }
    }
}

window.onload = load;

</script>
</head>
<body>
<svg id="svg" width="1500" height="2000">
    <g id="bg" width="1500" height="2000"></g>
    <g id="fg" width="1500" height="2000"></g>
</svg>
</body>
</html>
