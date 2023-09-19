const express = require('express');
const mustacheExpress = require('mustache-express');

const app = express();
app.use(express.json())
app.set('view engine', 'mustache');
app.engine('mustache', mustacheExpress());
const port = 8080;

app.get('/', (req, res) => {
    res.json({ status: "OK" });
});

app.post('/generate-html', (req, res) => {
    const data  = req.body
    res.render('index', { data }, function (err, html) {
        console.log(req);
        console.log(data);
        if (err) {
            res.status(500).json({ error: err });
        } else {
            res.send(html);
        }
    });
});

app.listen(port, () => {
    console.log(`HTML Insights app listening on port ${port}`);
});