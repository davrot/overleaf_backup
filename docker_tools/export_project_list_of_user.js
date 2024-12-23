const ProjectGetter = require('/overleaf/services/web/app/src/Features/Project/ProjectGetter');
const { waitForDb } = require('/overleaf/services/web/app/src/infrastructure/mongodb')
const ProjectController = require('/overleaf/services/web/app/src/Features/Project/ProjectController');
const fs = require('fs/promises'); 

async function main() {

    // // Get command-line arguments
    const args = process.argv.slice(2);
    if (args.length < 2) {
        console.error('Usage: node export_project_list_of_user.js <userId> <filename>');
        process.exit(1);
    }

    const userId = args[0];
    const filename = args[1];

    try {
        await waitForDb()
    } catch (err) {
        console.error('Cannot connect to mongodb')
        throw err
    }

    let projects = await ProjectGetter.promises.findAllUsersProjects(
        userId,
        'name lastUpdated publicAccesLevel archived trashed owner_ref'
    )

    projects = ProjectController._buildProjectList(projects, userId)
        .filter(p => !(p.archived || p.trashed))
        .map(p => ({ _id: p.id, name: p.name, accessLevel: p.accessLevel }))


    // Wrap the projects array in an object with a key name
    const data = { "projects": projects }; 

    // Write projects data to JSON file
    try {
        await fs.writeFile(filename, JSON.stringify(data, null, 2) + '\n');
        console.log('Projects written to JSON file successfully.');
    } catch (err) {
        console.error('Error writing projects to JSON file:', err);
        process.exit(1);
    }
    
    console.log('Done.'); // Use console.log for success messages
    process.exit(0);
}

main().catch(err => {
    console.error("An unexpected error occurred:", err); // Catch any unexpected errors
    process.exit(1);
});
