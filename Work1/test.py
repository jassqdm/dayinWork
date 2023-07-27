from sanic import Sanic
from sanic.response import json
from motor.motor_asyncio import AsyncIOMotorClient

app = Sanic(__name__)

mongodb_uri = "mongodb://localhost:27017"
database_name = '20212103843'  # 更改为您的数据库名称

class Database:
    def __init__(self, uri, database_name):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[database_name]

    async def insert(self, collection_name, document):
        collection = self.db[collection_name]
        await collection.insert_one(document)

    def find(self, collection_name, query=None):
        collection = self.db[collection_name]
        return collection.find(query)

    async def update(self, collection_name, query, update):
        collection = self.db[collection_name]
        await collection.update_many(query, update)

    async def delete(self, collection_name, query):
        collection = self.db[collection_name]
        await collection.delete_many(query)


db_instance = Database(mongodb_uri, database_name)


# 获取所有图书信息
@app.route("/books", methods=["GET"])
async def get_all_books(request):
    books = db_instance.find('books')
    return json([book async for book in books])

# 获取特定图书信息
@app.route("/book/<id>", methods=["GET"])
async def get_book(request, id):
    book = await db_instance.find('books', {'_id': id}).to_list(length=None)
    if book:
        return json(book)
    else:
        return json({'message': 'Book not found'}, status=404)
# 创建新的图书
@app.route("/book/create", methods=["POST"])
async def create_book(request):
    data = request.json
    await db_instance.insert('books', data)
    return json({'message': 'Book created successfully'})

# 更新图书信息
@app.route("/book/update/<id>", methods=["PUT"])
async def update_book(request, id):
    query = {'_id': id}
    update = {'$set': request.json}
    await db_instance.update('books', query, update)
    return json({'message': 'Book updated successfully'})

# 删除特定图书
@app.route("/book/delete/<id>", methods=["DELETE"])
async def delete_book(request, id):
    query = {'_id': id}
    await db_instance.delete('books', query)
    return json({'message': 'Book deleted successfully'})

# 运行应用
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
