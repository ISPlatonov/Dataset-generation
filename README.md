# Dataset generator

This is a simple dataset generator for ...

## Usage

```bash
python3 main.py
```

This is a desktop application, so you can see the interface.

## Dependencies

To install the dependencies, run:

```bash
pip3 install -r requirements.txt
```

## Configuration

The configuration file is `config.json`. You can change the parameters of the generator.

## Architecture

The architecture is based on the MVC pattern.

```mermaid
graph TB
    
    subgraph User
        user[main.py] --deploys--> main[main.qml]
    end
    subgraph View
        view(QML frontend)
    end
    subgraph Model
        images(images folder)
        generated_images(generated_images folder)
    end
    subgraph Controller
        Mngr[Manager.py]
        Mngr --calls--> HS[HandSegmentor.py]
        Mngr --calls--> BI(BackgroundImposing)
        Mngr --camera--> Cam[camera.qml]
        Mngr -.- Cfg[config.json]
    end
    
    main --interacts--> view
    view --uses--> Mngr
    Cam --creates--> images
    BI --creates--> generated_images
    HS --manipulates--> images
    images --updates--> view
    generated_images --updates--> view
    view --sees--> main
```