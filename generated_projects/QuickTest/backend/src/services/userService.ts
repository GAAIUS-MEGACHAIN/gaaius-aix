import prisma from '../config/database';

class UserserviceService {
  async list() {
    return await prisma.userservice.findMany();
  }

  async getById(id: string) {
    return await prisma.userservice.findUnique({
      where: { id },
    });
  }

  async create(data: any) {
    return await prisma.userservice.create({
      data,
    });
  }

  async update(id: string, data: any) {
    return await prisma.userservice.update({
      where: { id },
      data,
    });
  }

  async delete(id: string) {
    return await prisma.userservice.delete({
      where: { id },
    });
  }
}

export default new UserserviceService();

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation
