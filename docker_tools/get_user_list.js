const { waitForDb } = require('/overleaf/services/web/app/src/infrastructure/mongodb')
const { User } = require('/overleaf/services/web/app/src/models/User')


async function main() {
    
    try {
        await waitForDb()
    } catch (err) {
        console.error('Cannot connect to mongodb')
        process.exit(1); // fail
    }

    try {
        // Find all users and select only email and _id fields for efficiency
        const users = await User.find({}, 'email _id').exec()
        
        if (!users || users.length === 0) {
            console.error('No users')
            process.exit(1)
        }

        // Transform and output as JSON
        const userList = users.map(user => ({
            id: user._id.toString(),  // Convert ObjectId to string
            email: user.email
        }))

        const data = { "userlist": userList }; 
        
        console.log("#-#-#",JSON.stringify(data, null, 2),"#-#-#")  // Pretty print with 2-space indentation
        process.exit(0)

    } catch (err) {
        console.error('Error while fetching users:', err)
        process.exit(1)
    }

}

main().catch(err => {
    console.error("An unexpected error occurred:", err); // Catch any unexpected errors
    process.exit(1); // fail
});

