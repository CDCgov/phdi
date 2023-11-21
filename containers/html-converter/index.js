const express = require('express');
const mustacheExpress = require('mustache-express');
const multer = require('multer');
const os = require('os');
const fs = require('fs');

const upload = multer({dest: os.tmpdir()});

const app = express();
app.use(express.json())
app.set('view engine', 'mustache');
app.engine('mustache', mustacheExpress());
const port = 8080;

app.get('/', (req, res) => {
    res.json({status: "OK"});
});

app.post('/generate-html', upload.single('file'), (req, res) => {
    try {
        fs.readFile(req.file.path, (err, data) => {
            if (err) {
                res.status(500).json({error: err});
            } else {
                res.send(data);
            }
        });
    } catch (error) {
        console.log(error);
        res.status(500).json({error: 'Error reading file'});
    }
});

app.listen(port, () => {
    console.log(`HTML Insights app listening on port ${port}`);
});