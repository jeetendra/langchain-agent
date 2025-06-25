import asyncio

async def task1():
    async def set_future_value(fut):
        await asyncio.sleep(1)
        fut.set_result("done")

    async def main():
        fut = asyncio.Future()  # This is like a Promise
        asyncio.create_task(set_future_value(fut))  # simulate async operation
        result = await fut
        print(result)  # Output: done

    await main()

# asyncio.run(task1())


async def task2():
    async def async_task():
        await asyncio.sleep(5)
        return "result"

    async def main():
        result = await async_task()
        print(result)

    await main()

# asyncio.run(task2())

async def task3():
    async def task1():
        await asyncio.sleep(1)
        return "A"

    async def task2():
        await asyncio.sleep(1.5)
        return "B"

    async def main():
        results = await asyncio.gather(task1(), task2())
        print(results)
    await main()

asyncio.run(task3())