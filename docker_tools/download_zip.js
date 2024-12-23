const DocumentUpdaterHandler = require('/overleaf/services/web/app/src/Features/DocumentUpdater/DocumentUpdaterHandler')
const ProjectGetter = require('/overleaf/services/web/app/src/Features/Project/ProjectGetter');
const ProjectZipStreamManager = require('/overleaf/services/web/app/src/Features/Downloads/ProjectZipStreamManager')
const { waitForDb } = require('/overleaf/services/web/app/src/infrastructure/mongodb')
const fs = require('fs');

async function main() {

    // Get command-line arguments
    const args = process.argv.slice(2);
    if (args.length < 2) {
        console.error('Usage: node download_zip.js <projectId> <filename>');
        process.exit(1);
    }

    const projectId = args[0];
    const filename = args[1];

    try {
        await waitForDb()
    } catch (err) {
        console.error('Cannot connect to mongodb')
        throw err
    }
    
    try {
        await new Promise((resolve, reject) => {
            DocumentUpdaterHandler.flushProjectToMongo(projectId, (error, result) => {
                if (error) {
                    console.error("Error flushing project to Mongo:", error);
                    process.exit(1); // Exit if flushing fails
                } else {
                    resolve(result);
                }
            });
        });
    } catch (error) {
        console.error("Failed to flush project to Mongo:", error);
        process.exit(1); // Exit if flushing fails
    }

    try {
        await new Promise((resolve, reject) => {
            ProjectGetter.getProject(projectId, (error, project) => {
                if (error) {
                    console.error("Failed to get project:", error);
                    process.exit(1);
                } else {
                    resolve(project);
                }
            });
        });
    } catch (error) {
        console.error("Failed to get project:", error);
        process.exit(1);
    }

    let archive;
    try {
        archive = await new Promise((resolve, reject) => {
            ProjectZipStreamManager.createZipStreamForProject(projectId, (error, stream) => {
                if (error) {
                    console.error("Failed to create zip stream:", error);
                    process.exit(1);
                } else {
                    resolve(stream);
                }
            });
        });
    } catch(error) {
        console.error("Failed to create zip stream:", error);
        process.exit(1);
    }

    const output = fs.createWriteStream(filename);

    try {
        // Key change: Use a Promise to await the 'finish' event
        await new Promise((resolve, reject) => {
            archive.pipe(output);

            archive.on('error', reject); // Reject the promise on error
            output.on('error', reject); // Reject the promise on error
            output.on('finish', resolve); // Resolve the promise on finish
        });
    } catch (error) {
        console.error("Error during zip creation and writing:", error);
        process.exit(1);
    }
    console.log('Done.'); // Use console.log for success messages
    process.exit(0);
}

main().catch(err => {
    console.error("An unexpected error occurred:", err); // Catch any unexpected errors
    process.exit(1);
});
