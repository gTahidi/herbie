import asyncio
from dataclasses import dataclass
import shlex
import time
from python.helpers.tool import Tool, Response
from python.helpers import files
from python.helpers.print_style import PrintStyle
from python.helpers.docker import DockerContainerManager

@dataclass
class State:
    docker: DockerContainerManager

class CodeExecution(Tool):

    async def execute(self, **kwargs):
        await self.agent.handle_intervention()
        await self.prepare_state()
        
        runtime = self.args["runtime"].lower().strip()
        if runtime == "python":
            response = await self.execute_python_code(self.args["code"])
        elif runtime == "nodejs":
            response = await self.execute_nodejs_code(self.args["code"])
        elif runtime == "terminal":
            response = await self.execute_terminal_command(self.args["code"])
        elif runtime == "output":
            response = await self.get_docker_output(wait_with_output=5, wait_without_output=20)
        elif runtime == "reset":
            response = await self.reset_docker()
        else:
            response = self.agent.read_prompt("fw.code_runtime_wrong.md", runtime=runtime)

        if not response: response = self.agent.read_prompt("fw.code_no_output.md")
        return Response(message=response, break_loop=False)

    async def before_execution(self, **kwargs):
        await self.agent.handle_intervention()
        PrintStyle(font_color="#1B4F72", padding=True, background_color="white", bold=True).print(f"{self.agent.agent_name}: Using tool '{self.name}':")
        self.log = self.agent.context.log.log(type="code_exe", heading=f"{self.agent.agent_name}: Using tool '{self.name}':", content="", kvps=self.args)
        if self.args and isinstance(self.args, dict):
            for key, value in self.args.items():
                PrintStyle(font_color="#85C1E9", bold=True).stream(self.nice_key(key)+": ")
                PrintStyle(font_color="#85C1E9", padding=isinstance(value,str) and "\n" in value).stream(value)
                PrintStyle().print()

    async def after_execution(self, response, **kwargs):
        msg_response = self.agent.read_prompt("fw.tool_response.md", tool_name=self.name, tool_response=response.message)
        await self.agent.append_message(msg_response, human=True)

    async def prepare_state(self, reset=False):
        self.state = self.agent.get_data("cot_state")
        if not self.state or reset:
            docker = DockerContainerManager(
                logger=self.agent.context.log,
                name=self.agent.config.code_exec_docker_name,
                image=self.agent.config.code_exec_docker_image,
                ports=self.agent.config.code_exec_docker_ports,
                volumes=self.agent.config.code_exec_docker_volumes
            )
            docker.start_container()
            self.state = State(docker=docker)
        self.agent.set_data("cot_state", self.state)
    
    async def execute_python_code(self, code):
        escaped_code = shlex.quote(code)
        command = f'python3 -c {escaped_code}'
        return await self.docker_exec(command)

    async def execute_nodejs_code(self, code):
        escaped_code = shlex.quote(code)
        command = f'node -e {escaped_code}'
        return await self.docker_exec(command)

    async def execute_terminal_command(self, command):
        return await self.docker_exec(command)

    async def docker_exec(self, command):
        await self.agent.handle_intervention()
        
        full_command = f'docker exec {self.state.docker.name} {command}'
        process = await asyncio.create_subprocess_shell(
            full_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        PrintStyle(background_color="white", font_color="#1B4F72", bold=True).print(f"{self.agent.agent_name} code execution output:")
        return await self.get_docker_output(process)

    async def get_docker_output(self, process=None, wait_with_output=3, wait_without_output=10):
        if process is None:
            return "No process to read output from."

        output = []
        idle = 0
        SLEEP_TIME = 0.1

        while True:
            if process.stdout.at_eof() and process.stderr.at_eof():
                break

            await asyncio.sleep(SLEEP_TIME)
            stdout_data = await process.stdout.read(1024)
            stderr_data = await process.stderr.read(1024)

            await self.agent.handle_intervention()

            if stdout_data or stderr_data:
                output.append(stdout_data.decode())
                output.append(stderr_data.decode())
                PrintStyle(font_color="#85C1E9").stream(stdout_data.decode())
                PrintStyle(font_color="#E74C3C").stream(stderr_data.decode())
                self.log.update(content=''.join(output))
                idle = 0
            else:
                idle += 1
                if idle > (wait_with_output if output else wait_without_output) / SLEEP_TIME:
                    break

        await process.wait()
        return ''.join(output)

    async def reset_docker(self):
        await self.prepare_state(reset=True)
        return "Docker environment has been reset."