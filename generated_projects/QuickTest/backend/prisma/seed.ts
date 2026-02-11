import prisma from './client';

async function main() {
  console.log('Seeding database...');

  await prisma.user.createMany({
    data: [
      {{ email: 'admin@example.com', name: 'Admin', password: 'hashed', role: 'admin' }},
      {{ email: 'user@example.com', name: 'User', password: 'hashed', role: 'user' }},
    ],
  });

  console.log('Database seeded successfully');
}

main()
  .catch(e => {
    console.error(e);
    process.exit(1);
  });
