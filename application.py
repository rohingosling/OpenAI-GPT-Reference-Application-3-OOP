import os
from   datetime import datetime
from   openai   import OpenAI

class Application:

    MODEL_GPT_3_5_TURBO = 'gpt-3.5-turbo'
    MODEL_GPT_4         = 'gpt-4'
    MODEL_GPT_4O        = 'gpt-4o'

    CONSOLE_PROMPT_USER = '[User]'
    CONSOLE_PROMPT_AI   = '[AI]'

    COMMAND_NONE             = 0
    COMMAND_RUN              = 1
    COMMAND_EXIT_APPLICATION = 2

    #---------------------------------------------------------------------------------------------------------------------------------------------------------
    # Constructor.
    #---------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__ ( self ):

        self.client               = OpenAI ( api_key = os.environ [ 'OPENAI_API_KEY' ] )        
        self.model                = self.MODEL_GPT_4O
        self.max_tokens           = 1024
        self.temperature          = 0.7
        self.streaming_enabled    = True
        self.system_prompt        = 'You are an intelligent assistant. You always provide well-reasoned answers that are both correct and helpful.'
        self.conversation_history = [ { "role": "system", "content": self.system_prompt } ]
        self.command              = self.COMMAND_RUN
        self.chat_log_folder      = 'chat_log'

    #---------------------------------------------------------------------------------------------------------------------------------------------------------
    # Starts an instance of the applciation class.
    #---------------------------------------------------------------------------------------------------------------------------------------------------------

    def run ( self ):

        self.print_program_info ()
        self.main_loop ()

    #---------------------------------------------------------------------------------------------------------------------------------------------------------
    # Main loop of the chat bot. 
    #---------------------------------------------------------------------------------------------------------------------------------------------------------

    def main_loop ( self ):
        
        while self.command == self.COMMAND_RUN:
        
            user_input   = self.get_user_prompt ()
            self.command = self.get_application_command ( user_input )

            if self.command == self.COMMAND_RUN:

                self.conversation_history.append ( {"role": "user", "content": user_input} )
                response = self.get_language_model_response ( self.conversation_history, self.streaming_enabled )
                response = self.process_language_model_response ( response )
                self.conversation_history.append ( {"role": "assistant", "content": response} )

        self.save_chat_log_to_file ( self.conversation_history )

    #---------------------------------------------------------------------------------------------------------------------------------------------------------
    # Get input from the user. 
    #---------------------------------------------------------------------------------------------------------------------------------------------------------

    def get_user_prompt ( self ):

        user_input = input ( f"{self.CONSOLE_PROMPT_USER}\n" )
        return user_input
    
    #---------------------------------------------------------------------------------------------------------------------------------------------------------
    # Determine application command based on content of user prompt input.
    #---------------------------------------------------------------------------------------------------------------------------------------------------------

    def get_application_command ( self, user_input ):

        if user_input.lower () == "exit":
            return self.COMMAND_EXIT_APPLICATION
        else:
            return self.COMMAND_RUN
        
    #---------------------------------------------------------------------------------------------------------------------------------------------------------
    # Query language model. 
    #---------------------------------------------------------------------------------------------------------------------------------------------------------

    def get_language_model_response ( self, conversation_history, streaming_enabled = False ):

        try:
            response = self.client.chat.completions.create (
                model       = self.model,
                messages    = conversation_history,
                max_tokens  = self.max_tokens,
                temperature = self.temperature,
                stream      = self.streaming_enabled
            )

            if self.streaming_enabled:
                return response
            else:
                return response.choices [ 0 ].message.content

        except Exception as e:

            return f"\n[EXCEPTION] An error occurred: {str(e)}\n"
        
    #---------------------------------------------------------------------------------------------------------------------------------------------------------
    # Process language model response.
    # - Determin what do do with the response from the model.
    # - In this example we just write the response to the console, either streamed or not. 
    # - But if we wanted the output to be formatted as a JSON structure for example, we could use this method to interpret and process the results. 
    #---------------------------------------------------------------------------------------------------------------------------------------------------------

    def process_language_model_response ( self, response ):

        # Print AI prompt symbol. 

        print ( f"\n{self.CONSOLE_PROMPT_AI}" )

        # Handle the error message case

        if isinstance ( response, str ):            
            print ( response )
            return response
        
        # Handle normal response. 

        if self.streaming_enabled:

            response_stream = { "role": "assistant", "content": "" }
            
            for chunk in response:
                if chunk.choices [ 0 ].delta.content:
                    print ( chunk.choices [ 0 ].delta.content, end = "", flush = True )
                    response_stream [ "content" ] += chunk.choices [ 0 ].delta.content

            print ( "\n" )
            return response_stream [ "content" ]
        
        else:

            print ( f"{response}\n" )
            return response
        
    #---------------------------------------------------------------------------------------------------------------------------------------------------------
    # Print program information to the console. 
    #---------------------------------------------------------------------------------------------------------------------------------------------------------

    def print_program_info(self):

        print ()
        print ( 'Language Model:' )
        print ( f'- Model:             {self.model}' )
        print ( f'- Max Tokens:        {self.max_tokens}' )
        print ( f'- Temperature:       {self.temperature}' )
        print ( f'- Streaming Enabled: {self.streaming_enabled}' )
        print ()

    #---------------------------------------------------------------------------------------------------------------------------------------------------------
    # Save chat log to file. 
    #---------------------------------------------------------------------------------------------------------------------------------------------------------

    def save_chat_log_to_file ( self, conversation_history ):

        # Initalise the chat log folder name, and then create the folder if it does not already exist. 

        folder_path = self.chat_log_folder

        if not os.path.exists ( folder_path ):
            os.makedirs ( folder_path )

        # Incrament the file name index, and compile the file name. 

        file_index = 0
        while os.path.exists ( os.path.join ( folder_path, f'chat_log_{file_index}.txt' ) ):
            file_index += 1

        file_name = os.path.join ( folder_path, f'chat_log_{file_index}.txt' )

        # Write the model information and chat log to the file. 

        with open ( file_name, 'w', encoding = 'utf-8' ) as file:
            file.write ( f'Model:             {self.model}\n' )
            file.write ( f'Max Tokens:        {self.max_tokens}\n' )
            file.write ( f'Temperature:       {self.temperature}\n' )
            file.write ( f'Streaming Enabled: {self.streaming_enabled}\n' )
            file.write ( '\n' )

            for row in conversation_history:
                file.write ( f'[{row["role"]}]\n{row["content"]}\n\n' )

        # Let the user know that the file has been writen. 

        print ( f'\nConversation history saved to "{file_name}".' )
