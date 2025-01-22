// const { waitForDb } = require('/overleaf/services/web/app/src/infrastructure/mongodb')
const { User } = require('/overleaf/services/web/app/src/models/User')


async function main() {

    const args = process.argv.slice(2);
    if (args.length < 1) {
        console.error('Usage: node id_user.js <username>');
        process.exit(1);
    }

    const username = args[0];
    const query =  {"email": username };
    
//    try {
//        await waitForDb()
//    } catch (err) {
//        console.error('Cannot connect to mongodb')
//        process.exit(1); // fail
//    }

    const user = await User.findOne(query).exec();

    if (!user || !user._id) {
        process.exit(1); // fail
    }    
    console.log("#-#-#",user._id,"#-#-#")
    process.exit(0);
}

main().catch(err => {
    console.error("An unexpected error occurred:", err); // Catch any unexpected errors
    process.exit(1); // fail
});

