const express = require('express');
const mustacheExpress = require('mustache-express');
const multer  = require('multer');
const os  = require('os');
const fs = require('fs');
const csv=require('csvtojson');

const upload = multer({ dest: os.tmpdir() });

const app = express();
app.use(express.json())
app.set('view engine', 'mustache');
app.engine('mustache', mustacheExpress());
const port = 8080;

app.get('/', (req, res) => {
    res.json({ status: "OK" });
});

app.post('/generate-html', upload.single('file'), (req, res) => {
    csv()
        .fromFile(req.file.path)
        .then((csv_data) => {
            res.render('index', { csv_data }, function (err, html) {
                if (err) {
                    res.status(500).json({ error: err });
                } else {
                    res.send(html);
                }
            });
        })
        .catch((err) => {
            res.status(500).json({ error: 'Error parsing CSV file' });
        });
});

app.listen(port, () => {
    console.log(`HTML Insights app listening on port ${port}`);
});