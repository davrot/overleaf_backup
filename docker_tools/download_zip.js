const ProjectEntityHandler = require('/overleaf/services/web/app/src/Features/Project/ProjectEntityHandler')
const DocumentUpdaterHandler = require('/overleaf/services/web/app/src/Features/DocumentUpdater/DocumentUpdaterHandler')
const { waitForDb } = require('/overleaf/services/web/app/src/infrastructure/mongodb')
const archiver = require('/overleaf/node_modules/archiver')
const ProjectGetter = require('/overleaf/services/web/app/src/Features/Project/ProjectGetter');
const settings = require('/overleaf/node_modules/@overleaf/settings')
const fs = require('fs');
const { promisify } = require('util');

async function main() {
    
    
    // Get command-line arguments
    const args = process.argv.slice(2);
    if (args.length < 2) {
        console.error('Usage: node download_zip_time.js <projectId> <filename> [<timestamp>]');
        process.exit(1);
    }

    const projectId = args[0];
    const output_filename = args[1];
    let time_filter_active = false;
    let referenceDate;

    // Check if reference date parameter was provided
    if (args.length >= 3) {
        try {
            referenceDate = new Date(args[2]);
            if (isNaN(referenceDate.getTime())) {
                console.error('Error: Invalid date format provided');
                process.exit(1);
            }
            time_filter_active = true;
        } catch (error) {
            console.error('Error: Invalid date format provided');
            process.exit(1);
        }
    }

    try {
        await waitForDb();

        // Flush project to MongoDB
        await new Promise((resolve, reject) => {
            DocumentUpdaterHandler.flushProjectToMongo(projectId, (error) => {
                if (error) process.exit(1);
                else resolve();
            });
        });

        // Get project info
        const project_info = await new Promise((resolve, reject) => {
            ProjectGetter.getProject(projectId, {
                'overleaf.history.id': true,
            }, (error, project) => {
                if (error) process.exit(1);
                else resolve(project);
            });
        });

        // Get all files
        let list_files = await new Promise((resolve, reject) => {
            ProjectEntityHandler.getAllFiles(projectId, (error, result) => {
                if (error) process.exit(1);
                else resolve(result);
            });
        });

        if (time_filter_active) {
            list_files = Object.fromEntries(
                Object.entries(list_files).filter(([_, value]) => 
                    value.created > referenceDate
                )
            );    
        }

        // Get all docs
        const list_docs = await new Promise((resolve, reject) => {
            ProjectEntityHandler.getAllDocs(projectId, (error, result) => {
                if (error) process.exit(1);
                else resolve(result);
            });
        });

        // Create archive
        const archive = archiver('zip', {
            zlib: { level: 0 }
        });

        // Create write stream
        const output = fs.createWriteStream(output_filename);
        
        // Set up archive error handling
        archive.on('error', err => {
            console.log('Archive error:', err);
            process.exit(1);
        });

        archive.on('warning', err => {
            if (err.code === 'ENOENT') {
                console.log('Archive warning:', err);
            } 
            process.exit(1);
        });

        // Create promise for output stream
        const outputFinished = new Promise((resolve, reject) => {
            output.on('close', resolve);
            output.on('error', reject);
        });

        // Pipe archive to output file
        archive.pipe(output);

        // Add documents to archive
        for (const [path, doc] of Object.entries(list_docs)) {
            const cleanPath = path.startsWith('/') ? path.slice(1) : path;
            console.log('Adding doc', { path: cleanPath });
            archive.append(doc.lines.join('\n'), { name: cleanPath });
        }

        // Add files to archive using promises
        const filePromises = Object.entries(list_files).map(async ([path, file]) => {
            const cleanPath = path.startsWith('/') ? path.slice(1) : path;
            try {
                console.log('Adding file', { path: cleanPath });
                url = new URL(settings.apis.filestore.url)
                url.pathname = `/project/${projectId}/file/${file._id}`                
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const buffer = await response.arrayBuffer();
                archive.append(Buffer.from(buffer), { name: cleanPath });
                return Promise.resolve();
            } catch (err) {
                console.warn(`File not found: ${cleanPath}`, err);
                return Promise.resolve();
            }
        });

        // Wait for all files to be processed
        await Promise.all(filePromises);

        // Finalize the archive
        await archive.finalize();

        // Wait for the output file to be fully written
        await outputFinished;

        console.log('Done.');
        process.exit(0);

    } catch (error) {
        console.error("An error occurred:", error);
        process.exit(1);
    }
}

main();

