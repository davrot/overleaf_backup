const { waitForDb } = require('/overleaf/services/web/app/src/infrastructure/mongodb')
const { User } = require('/overleaf/services/web/app/src/models/User')
const bcrypt = require('/overleaf/services/web/node_modules/bcrypt')

async function main() {

    const args = process.argv.slice(2);
    if (args.length < 2) {
        console.error('Usage: node auth_check_user.js <username> <password>');
        process.exit(1);
    }

    const username = args[0];
    const password = args[1];
    const query =  {"email": username };
    
    try {
        await waitForDb()
    } catch (err) {
        console.error('Cannot connect to mongodb')
        process.exit(1); // fail
    }

    const user = await User.findOne(query).exec();

    if (!user || !user.hashedPassword) {
        process.exit(1); // fail
    }    

    let rounds = 0
    try {
        rounds = bcrypt.getRounds(user.hashedPassword)
    } catch (err) {
        let prefix, suffix, length
        if (typeof user.hashedPassword === 'string') {
            length = user.hashedPassword.length
            if (user.hashedPassword.length > 50) {
                // A full bcrypt hash is 60 characters long.
                prefix = user.hashedPassword.slice(0, '$2a$12$x'.length)
                suffix = user.hashedPassword.slice(-4)
            } else if (user.hashedPassword.length > 20) {
                prefix = user.hashedPassword.slice(0, 4)
                suffix = user.hashedPassword.slice(-4)
            } else {
                prefix = user.hashedPassword.slice(0, 4)
            }
        }

        process.exit(1); // fail
    }

    const match = await bcrypt.compare(password, user.hashedPassword)

    if (match) {
        process.exit(0);
    }
    else {
        process.exit(1); // fail
    }
}

main().catch(err => {
    console.error("An unexpected error occurred:", err); // Catch any unexpected errors
    process.exit(1); // fail
});

